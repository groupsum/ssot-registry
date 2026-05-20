from __future__ import annotations

from pathlib import Path
from typing import Any

from ssot_registry.control.service import ControlPlane


def _plane(repo: str) -> ControlPlane:
    return ControlPlane(Path(repo))


def claim_next_maturation_slice(
    repo: str,
    worker_id: str,
    campaign_id: str,
    target_tier: str = "T2",
    os_user: str | None = None,
    ttl_seconds: int = 1800,
) -> dict[str, Any]:
    return _plane(repo).claim_next_maturation_slice(
        worker_id=worker_id,
        campaign_id=campaign_id,
        target_tier=target_tier,
        os_user=os_user,
        ttl_seconds=ttl_seconds,
    )


def renew_lease(repo: str, worker_id: str, lease_id: str, fencing_token: int, ttl_seconds: int = 1800) -> dict[str, Any]:
    return _plane(repo).renew_lease(
        worker_id=worker_id,
        lease_id=lease_id,
        fencing_token=fencing_token,
        ttl_seconds=ttl_seconds,
    )


def get_slice_context(repo: str, lease_id: str) -> dict[str, Any]:
    return _plane(repo).get_slice_context(lease_id)


def complete_slice(repo: str, worker_id: str, lease_id: str, fencing_token: int, result: dict[str, Any]) -> dict[str, Any]:
    return _plane(repo).complete_slice(worker_id=worker_id, lease_id=lease_id, fencing_token=fencing_token, result=result)


def abandon_slice(repo: str, worker_id: str, lease_id: str, fencing_token: int, reason: str) -> dict[str, Any]:
    return _plane(repo).abandon_slice(worker_id=worker_id, lease_id=lease_id, fencing_token=fencing_token, reason=reason)


def get_campaign_status(repo: str, campaign_id: str, target_tier: str = "T2") -> dict[str, Any]:
    return _plane(repo).get_campaign_status(campaign_id, target_tier=target_tier)


def get_worker_events(
    repo: str,
    worker_id: str | None = None,
    campaign_id: str | None = None,
    after_event_id: int = 0,
    limit: int = 100,
) -> dict[str, Any]:
    return _plane(repo).get_worker_events(
        worker_id=worker_id,
        campaign_id=campaign_id,
        after_event_id=after_event_id,
        limit=limit,
    )


def ack_worker_events(repo: str, worker_id: str, event_ids: list[int], action: str = "processed") -> dict[str, Any]:
    return _plane(repo).ack_worker_events(worker_id=worker_id, event_ids=event_ids, action=action)


def get_conflicts(repo: str, status: str | None = "open") -> dict[str, Any]:
    return _plane(repo).get_conflicts(status=status)
