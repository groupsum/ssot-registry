from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from ssot_registry.api.load import load_registry
from ssot_registry.control.models import (
    EVENT_ERROR,
    EVENT_INFO,
    EVENT_WARN,
    LEASE_ACTIVE,
    REFRESH_CONTEXT,
    RENEW_LEASE,
    STOP_CURRENT_WORK,
    WORK_MAY_BE_AVAILABLE,
)
from ssot_registry.guards.completion import evaluate_completion_guard
from ssot_registry.maturation.selector import campaign_completion, next_maturation_slice, registry_content_hash
from ssot_registry.util.time import utc_now_iso

from .sqlite_store import ControlStore


def _future_iso(seconds: int) -> str:
    return (datetime.now(timezone.utc).replace(microsecond=0) + timedelta(seconds=seconds)).isoformat().replace("+00:00", "Z")


class ControlPlane:
    """Core service used by CLI, MCP, and tests for pull-worker coordination."""

    def __init__(self, repo_root: str | Path, *, store: ControlStore | None = None) -> None:
        self.repo_root = Path(repo_root)
        self.store = store or ControlStore(self.repo_root)
        self.store.initialize()

    def _registry(self) -> dict[str, Any]:
        _registry_path, _repo_root, registry = load_registry(self.repo_root)
        return registry

    def register_worker(self, worker_id: str, os_user: str | None = None) -> dict[str, Any]:
        worker = self.store.register_worker(worker_id, os_user=os_user)
        self.store.emit_event("worker_registered", worker_id=worker_id, payload=worker)
        return {"passed": True, "worker": worker}

    def claim_next_maturation_slice(
        self,
        *,
        worker_id: str,
        campaign_id: str,
        target_tier: str = "T2",
        os_user: str | None = None,
        ttl_seconds: int = 1800,
    ) -> dict[str, Any]:
        registry = self._registry()
        self.store.register_worker(worker_id, os_user=os_user)
        self.store.ensure_campaign(campaign_id, target_tier)
        active_roots = [row["path"] for row in self.store.active_path_leases()]
        selected = next_maturation_slice(registry, target_tier=target_tier, repo_root=self.repo_root, active_path_roots=active_roots)
        status = self.store.campaign_status(campaign_id)
        completion = campaign_completion(
            registry,
            target_tier=target_tier,
            repo_root=self.repo_root,
            active_lease_count=status["active_lease_count"],
        )
        if selected is None:
            if completion["complete"]:
                self.store.mark_campaign_complete(campaign_id)
                return {"passed": True, "kind": "campaign_complete", "campaign": completion}
            return {"passed": True, "kind": "no_work", "campaign": completion}

        lease = self.store.create_maturation_lease(
            campaign_id=campaign_id,
            worker_id=worker_id,
            feature_id=selected["feature_id"],
            from_tier=selected["from_tier"],
            to_tier=selected["to_tier"],
            path_roots=selected["path_roots"],
            registry_hash_at_claim=registry_content_hash(registry),
            expires_at=_future_iso(ttl_seconds),
        )
        lease = self.store.activate_lease(lease["lease_id"])
        self.store.emit_event(
            "maturation_lease_acquired",
            campaign_id=campaign_id,
            worker_id=worker_id,
            lease_id=lease["lease_id"],
            payload={
                "feature_id": lease["feature_id"],
                "transition": f"{lease['from_tier']}->{lease['to_tier']}",
                "path_roots": lease["path_roots"],
            },
        )
        return {"passed": True, "kind": "lease_granted", "lease": lease}

    def get_slice_context(self, lease_id: str) -> dict[str, Any]:
        registry = self._registry()
        lease = self.store.get_lease(lease_id)
        if lease is None:
            raise ValueError(f"unknown lease: {lease_id}")
        feature_id = lease["feature_id"]
        feature = next((row for row in registry.get("features", []) if row.get("id") == feature_id), None)
        claims = [
            row
            for row in registry.get("claims", [])
            if row.get("id") in set(feature.get("claim_ids", []) if isinstance(feature, dict) else [])
        ]
        tests = [
            row
            for row in registry.get("tests", [])
            if row.get("id") in set(feature.get("test_ids", []) if isinstance(feature, dict) else [])
        ]
        evidence = [
            row
            for row in registry.get("evidence", [])
            if row.get("id") in {item for claim in claims for item in claim.get("evidence_ids", [])}
        ]
        return {
            "passed": True,
            "lease": lease,
            "feature": feature,
            "claims": claims,
            "tests": tests,
            "evidence": evidence,
            "forbidden_paths": [".git/**", ".ssot/registry.json", ".ssot/registry.json.lock", ".ssot/control/**"],
        }

    def renew_lease(self, *, worker_id: str, lease_id: str, fencing_token: int, ttl_seconds: int = 1800) -> dict[str, Any]:
        lease = self.store.renew_lease(lease_id, worker_id, fencing_token, _future_iso(ttl_seconds))
        self.store.emit_event(
            "maturation_lease_renewed",
            campaign_id=lease["campaign_id"],
            worker_id=worker_id,
            lease_id=lease_id,
            recommended_action=RENEW_LEASE,
            payload={"expires_at": lease["expires_at"]},
        )
        return {"passed": True, "lease": lease}

    def abandon_slice(self, *, worker_id: str, lease_id: str, fencing_token: int, reason: str) -> dict[str, Any]:
        lease = self.store.abandon_lease(lease_id, worker_id, fencing_token, reason)
        self.store.emit_event(
            "maturation_lease_abandoned",
            campaign_id=lease["campaign_id"],
            worker_id=worker_id,
            lease_id=lease_id,
            severity=EVENT_WARN,
            recommended_action=WORK_MAY_BE_AVAILABLE,
            payload={"reason": reason, "feature_id": lease["feature_id"]},
        )
        return {"passed": True, "lease": lease}

    def complete_slice(self, *, worker_id: str, lease_id: str, fencing_token: int, result: dict[str, Any]) -> dict[str, Any]:
        registry = self._registry()
        lease = self.store.get_lease(lease_id)
        if lease is None:
            raise ValueError(f"unknown lease: {lease_id}")
        if lease["status"] != LEASE_ACTIVE:
            raise ValueError(f"lease is not active: {lease['status']}")
        if lease["worker_id"] != worker_id or int(lease["fencing_token"]) != int(fencing_token):
            raise ValueError("worker does not own lease or fencing token is stale")

        completion = evaluate_completion_guard(registry, lease, result, repo_root=self.repo_root)
        gate_result = completion.get("gate_result")
        if isinstance(gate_result, dict):
            self.store.record_gate_report(lease_id=lease_id, feature_id=lease["feature_id"], gate_result=gate_result)
        if not completion["passed"]:
            self.store.emit_event(
                "tier_gate_failed",
                campaign_id=lease["campaign_id"],
                worker_id=worker_id,
                lease_id=lease_id,
                severity=EVENT_ERROR,
                recommended_action=STOP_CURRENT_WORK,
                payload=completion,
            )
            return {"passed": False, "lease": lease, "completion": completion}

        finished = self.store.complete_lease(lease_id, worker_id, fencing_token, result)
        self.store.emit_event(
            "tier_gate_passed",
            campaign_id=finished["campaign_id"],
            worker_id=worker_id,
            lease_id=lease_id,
            recommended_action=REFRESH_CONTEXT,
            payload={"feature_id": finished["feature_id"], "approved_tier": result.get("requested_tier", finished["to_tier"])},
        )
        self.store.emit_event(
            "maturation_lease_completed",
            campaign_id=finished["campaign_id"],
            worker_id=worker_id,
            lease_id=lease_id,
            recommended_action=WORK_MAY_BE_AVAILABLE,
            payload={"feature_id": finished["feature_id"]},
        )
        return {"passed": True, "lease": finished, "completion": completion}

    def expire_due_leases(self) -> dict[str, Any]:
        expired = self.store.expire_due_leases(utc_now_iso())
        for lease in expired:
            self.store.emit_event(
                "lease_expired",
                campaign_id=lease["campaign_id"],
                worker_id=lease["worker_id"],
                lease_id=lease["lease_id"],
                severity=EVENT_WARN,
                recommended_action=STOP_CURRENT_WORK,
                payload={"feature_id": lease["feature_id"]},
            )
        return {"passed": True, "expired": expired}

    def get_campaign_status(self, campaign_id: str, target_tier: str = "T2") -> dict[str, Any]:
        registry = self._registry()
        status = self.store.campaign_status(campaign_id)
        completion = campaign_completion(
            registry,
            target_tier=target_tier,
            repo_root=self.repo_root,
            active_lease_count=status["active_lease_count"],
        )
        return {"passed": True, **status, "completion": completion}

    def get_worker_events(
        self,
        *,
        worker_id: str | None = None,
        campaign_id: str | None = None,
        after_event_id: int = 0,
        limit: int = 100,
    ) -> dict[str, Any]:
        return {
            "passed": True,
            "events": self.store.get_events(
                worker_id=worker_id,
                campaign_id=campaign_id,
                after_event_id=after_event_id,
                limit=limit,
            ),
        }

    def ack_worker_events(self, *, worker_id: str, event_ids: list[int], action: str = "processed") -> dict[str, Any]:
        return self.store.ack_events(worker_id, event_ids, action)

    def get_conflicts(self, status: str | None = "open") -> dict[str, Any]:
        return {"passed": True, "conflicts": self.store.get_conflicts(status=status)}

    def notify_registry_updated(self, *, campaign_id: str | None = None, lease_id: str | None = None, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        event = self.store.emit_event(
            "registry_updated",
            campaign_id=campaign_id,
            lease_id=lease_id,
            severity=EVENT_INFO,
            recommended_action=REFRESH_CONTEXT,
            payload=payload or {},
        )
        return {"passed": True, "event": event}
