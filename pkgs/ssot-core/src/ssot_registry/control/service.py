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
from ssot_registry.control.scaffold import scaffold_target_claim_wiring
from ssot_registry.guards.completion import evaluate_completion_guard
from ssot_registry.maturation.selector import campaign_completion, next_maturation_slice, registry_content_hash, slice_actionability
from ssot_registry.util.time import utc_now_iso

from .sqlite_store import ControlStore


def _future_iso(seconds: int) -> str:
    return (datetime.now(timezone.utc).replace(microsecond=0) + timedelta(seconds=seconds)).isoformat().replace("+00:00", "Z")


def _is_structural_block_reason(reason: str) -> bool:
    normalized = reason.lower()
    return any(
        marker in normalized
        for marker in (
            "missing target-tier claim",
            "missing target tier claim",
            "no linked",
            "lease forbids registry",
            "registry edits",
            "registry wiring",
            "claim wiring",
        )
    )


def _as_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


class ControlPlane:
    """Core service used by CLI, MCP, and tests for pull-worker coordination."""

    def __init__(self, repo_root: str | Path, *, store: ControlStore | None = None) -> None:
        self.repo_root = Path(repo_root)
        self.store = store or ControlStore(self.repo_root)
        self.store.initialize()

    def _registry(self) -> dict[str, Any]:
        _registry_path, _repo_root, registry = load_registry(self.repo_root)
        return registry

    def _resolve_scope_feature_ids(
        self,
        registry: dict[str, Any],
        *,
        feature_ids: list[str] | None = None,
        profile_ids: list[str] | None = None,
        boundary_ids: list[str] | None = None,
        campaign: dict[str, Any] | None = None,
    ) -> set[str] | None:
        metadata = campaign.get("metadata") if isinstance(campaign, dict) else {}
        metadata = metadata if isinstance(metadata, dict) else {}
        requested_features = feature_ids if feature_ids is not None else _as_string_list(metadata.get("feature_ids"))
        requested_profiles = profile_ids if profile_ids is not None else _as_string_list(metadata.get("profile_ids"))
        requested_boundaries = boundary_ids if boundary_ids is not None else _as_string_list(metadata.get("boundary_ids"))
        if not requested_features and not requested_profiles and not requested_boundaries:
            return None

        features = {row["id"]: row for row in registry.get("features", []) if isinstance(row, dict) and isinstance(row.get("id"), str)}
        profiles = {row["id"]: row for row in registry.get("profiles", []) if isinstance(row, dict) and isinstance(row.get("id"), str)}
        boundaries = {row["id"]: row for row in registry.get("boundaries", []) if isinstance(row, dict) and isinstance(row.get("id"), str)}
        resolved: set[str] = {feature_id for feature_id in requested_features if feature_id in features}

        def add_profile(profile_id: str, seen: set[str] | None = None) -> None:
            seen = seen or set()
            if profile_id in seen:
                return
            seen.add(profile_id)
            profile = profiles.get(profile_id)
            if not profile:
                return
            resolved.update(feature_id for feature_id in _as_string_list(profile.get("feature_ids")) if feature_id in features)
            for child_profile_id in _as_string_list(profile.get("profile_ids")):
                add_profile(child_profile_id, seen)

        for profile_id in requested_profiles:
            add_profile(profile_id)
        for boundary_id in requested_boundaries:
            boundary = boundaries.get(boundary_id)
            if not boundary:
                continue
            resolved.update(feature_id for feature_id in _as_string_list(boundary.get("feature_ids")) if feature_id in features)
            for profile_id in _as_string_list(boundary.get("profile_ids")):
                add_profile(profile_id)
        return resolved

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
        feature_ids: list[str] | None = None,
        profile_ids: list[str] | None = None,
        boundary_ids: list[str] | None = None,
        max_blockers_per_claim: int = 5,
        auto_scaffold: bool = False,
    ) -> dict[str, Any]:
        registry = self._registry()
        self.store.register_worker(worker_id, os_user=os_user)
        metadata = {
            key: value
            for key, value in {
                "feature_ids": feature_ids,
                "profile_ids": profile_ids,
                "boundary_ids": boundary_ids,
            }.items()
            if value is not None
        }
        campaign_row = self.store.ensure_campaign(campaign_id, target_tier, metadata=metadata or None)
        scope_feature_ids = self._resolve_scope_feature_ids(
            registry,
            feature_ids=feature_ids,
            profile_ids=profile_ids,
            boundary_ids=boundary_ids,
            campaign=campaign_row,
        )
        selected: dict[str, Any] | None = None
        blocked_in_call: list[dict[str, Any]] = []
        scaffolded_in_call: list[dict[str, Any]] = []
        while True:
            active_roots = [row["path"] for row in self.store.active_path_leases()]
            blocked = self.store.get_blocked_transitions(campaign_id)
            selected = next_maturation_slice(
                registry,
                target_tier=target_tier,
                repo_root=self.repo_root,
                active_path_roots=active_roots,
                blocked_transitions=blocked,
                scope_feature_ids=scope_feature_ids,
            )
            if selected is None:
                break
            actionability = slice_actionability(registry, selected, repo_root=self.repo_root)
            if actionability["passed"]:
                break
            if auto_scaffold and actionability.get("reason") == "missing_target_tier_claim_wiring":
                scaffold = scaffold_target_claim_wiring(self.repo_root, selected["feature_id"], selected["to_tier"])
                scaffolded_in_call.append(scaffold)
                if scaffold.get("passed"):
                    self.store.emit_event(
                        "registry_scaffolded",
                        campaign_id=campaign_id,
                        worker_id=worker_id,
                        severity=EVENT_INFO,
                        recommended_action=REFRESH_CONTEXT,
                        payload=scaffold,
                    )
                    registry = self._registry()
                    continue
            blocked_transition = self.store.record_blocked_transition(
                campaign_id=campaign_id,
                feature_id=selected["feature_id"],
                from_tier=selected["from_tier"],
                to_tier=selected["to_tier"],
                reason=str(actionability["reason"]),
                failures=[str(item) for item in actionability.get("failures", [])],
            )
            blocked_in_call.append(blocked_transition)
            self.store.emit_event(
                "maturation_transition_blocked",
                campaign_id=campaign_id,
                worker_id=worker_id,
                severity=EVENT_WARN,
                recommended_action="operator_repair_required",
                payload={"selected": selected, "actionability": actionability, "blocked_transition": blocked_transition},
            )
            if len(blocked_in_call) >= max(1, int(max_blockers_per_claim)):
                selected = None
                break

        status = self.store.campaign_status(campaign_id)
        completion = campaign_completion(
            registry,
            target_tier=target_tier,
            repo_root=self.repo_root,
            active_lease_count=status["active_lease_count"],
            scope_feature_ids=scope_feature_ids,
        )
        if selected is None:
            open_blocked = self.store.get_blocked_transitions(campaign_id)
            if open_blocked:
                return {
                    "passed": False,
                    "kind": "blocked",
                    "campaign": completion,
                    "blocked_transitions": open_blocked,
                    "blocked_in_call": blocked_in_call,
                    "scaffolded_in_call": scaffolded_in_call,
                }
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
        blocked_transition = None
        if _is_structural_block_reason(reason):
            blocked_transition = self.store.record_blocked_transition(
                campaign_id=lease["campaign_id"],
                feature_id=lease["feature_id"],
                from_tier=lease["from_tier"],
                to_tier=lease["to_tier"],
                reason="worker_reported_structural_blocker",
                failures=[reason],
            )
        self.store.emit_event(
            "maturation_lease_abandoned",
            campaign_id=lease["campaign_id"],
            worker_id=worker_id,
            lease_id=lease_id,
            severity=EVENT_WARN,
            recommended_action="operator_repair_required" if blocked_transition else WORK_MAY_BE_AVAILABLE,
            payload={"reason": reason, "feature_id": lease["feature_id"], "blocked_transition": blocked_transition},
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
        blockers = self.store.get_blocked_transitions(campaign_id)
        scope_feature_ids = self._resolve_scope_feature_ids(registry, campaign=status.get("campaign"))
        completion = campaign_completion(
            registry,
            target_tier=target_tier,
            repo_root=self.repo_root,
            active_lease_count=status["active_lease_count"],
            scope_feature_ids=scope_feature_ids,
        )
        summary = {
            "complete": completion["complete"],
            "target_tier": completion["target_tier"],
            "incomplete_count": len(completion["incomplete"]),
            "out_of_bounds_count": len(completion["out_of_bounds"]),
            "active_lease_count": completion["active_lease_count"],
            "blocked_transition_count": len(blockers),
        }
        incomplete_preview = completion["incomplete"][:25]
        return {
            "passed": True,
            **status,
            "summary": summary,
            "completion": {**completion, "incomplete": incomplete_preview, "incomplete_truncated": len(completion["incomplete"]) > len(incomplete_preview)},
            "blocked_transitions": blockers,
        }

    def scaffold_target_claim_wiring(self, *, feature_id: str, target_tier: str = "T1") -> dict[str, Any]:
        result = scaffold_target_claim_wiring(self.repo_root, feature_id, target_tier)
        if result.get("passed"):
            self.notify_registry_updated(payload={"source": "ssot-mcp", "tool": "scaffold_target_claim_wiring", "feature_id": feature_id, "target_tier": target_tier})
        return result

    def repair_blocked_transition(self, *, blocked_id: str) -> dict[str, Any]:
        blockers = self.store.get_blocked_transitions(status="open")
        blocker = next((item for item in blockers if item.get("blocked_id") == blocked_id), None)
        if blocker is None:
            raise ValueError(f"unknown open blocked transition: {blocked_id}")
        scaffold = self.scaffold_target_claim_wiring(feature_id=blocker["feature_id"], target_tier=blocker["to_tier"])
        if not scaffold.get("passed"):
            return {"passed": False, "blocked_transition": blocker, "scaffold": scaffold}
        resolved = self.store.resolve_blocked_transition(blocked_id, reason="registry_scaffolded")
        self.store.emit_event(
            "maturation_transition_repaired",
            campaign_id=resolved.get("campaign_id"),
            severity=EVENT_INFO,
            recommended_action=WORK_MAY_BE_AVAILABLE,
            payload={"blocked_transition": resolved, "scaffold": scaffold},
        )
        return {"passed": True, "blocked_transition": resolved, "scaffold": scaffold}

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
