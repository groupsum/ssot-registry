from __future__ import annotations

from pathlib import Path
from typing import Any

from ssot_registry.control.service import ControlPlane

_PINNED_REPO: Path | None = None


def configure_repo(repo: str | Path | None) -> None:
    global _PINNED_REPO
    _PINNED_REPO = Path(repo).resolve() if repo is not None else None


def resolve_repo(repo: str | None = None) -> Path:
    if _PINNED_REPO is None:
        if repo is None:
            raise ValueError("repo is required unless ssot-mcp is started with --repo")
        return Path(repo).resolve()
    if repo is not None and Path(repo).resolve() != _PINNED_REPO:
        raise ValueError(f"ssot-mcp is pinned to {_PINNED_REPO}; refusing repo {Path(repo).resolve()}")
    return _PINNED_REPO


def _plane(repo: str | None = None) -> ControlPlane:
    return ControlPlane(resolve_repo(repo))


def claim_next_maturation_slice(
    repo: str | None = None,
    worker_id: str = "",
    campaign_id: str = "",
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


def renew_lease(repo: str | None = None, worker_id: str = "", lease_id: str = "", fencing_token: int = 0, ttl_seconds: int = 1800) -> dict[str, Any]:
    return _plane(repo).renew_lease(
        worker_id=worker_id,
        lease_id=lease_id,
        fencing_token=fencing_token,
        ttl_seconds=ttl_seconds,
    )


def get_slice_context(repo: str | None = None, lease_id: str = "") -> dict[str, Any]:
    return _plane(repo).get_slice_context(lease_id)


def complete_slice(repo: str | None = None, worker_id: str = "", lease_id: str = "", fencing_token: int = 0, result: dict[str, Any] | None = None) -> dict[str, Any]:
    if result is None:
        result = {}
    return _plane(repo).complete_slice(worker_id=worker_id, lease_id=lease_id, fencing_token=fencing_token, result=result)


def abandon_slice(repo: str | None = None, worker_id: str = "", lease_id: str = "", fencing_token: int = 0, reason: str = "") -> dict[str, Any]:
    return _plane(repo).abandon_slice(worker_id=worker_id, lease_id=lease_id, fencing_token=fencing_token, reason=reason)


def get_campaign_status(repo: str | None = None, campaign_id: str = "", target_tier: str = "T2") -> dict[str, Any]:
    return _plane(repo).get_campaign_status(campaign_id, target_tier=target_tier)


def get_worker_events(
    repo: str | None = None,
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


def ack_worker_events(repo: str | None = None, worker_id: str = "", event_ids: list[int] | None = None, action: str = "processed") -> dict[str, Any]:
    if event_ids is None:
        event_ids = []
    return _plane(repo).ack_worker_events(worker_id=worker_id, event_ids=event_ids, action=action)


def get_conflicts(repo: str | None = None, status: str | None = "open") -> dict[str, Any]:
    return _plane(repo).get_conflicts(status=status)
