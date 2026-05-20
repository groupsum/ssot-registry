from __future__ import annotations

from pathlib import Path

import pytest

from ssot_mcp.tools import (
    abandon_slice,
    ack_worker_events,
    claim_next_maturation_slice,
    complete_slice,
    get_campaign_status,
    get_slice_context,
    get_worker_events,
    renew_lease,
)

from .test_worker_control_plane import _registry, _write_registry


def test_mcp_tools_delegate_to_control_plane(tmp_path: Path) -> None:
    _write_registry(tmp_path, _registry(tmp_path, t1_ready=False, t2_ready=False))

    response = claim_next_maturation_slice(
        repo=str(tmp_path),
        worker_id="worker-01",
        campaign_id="camp:test",
        target_tier="T2",
    )

    assert response["kind"] == "lease_granted"
    events = get_worker_events(repo=str(tmp_path), worker_id="worker-01")
    assert any(event["kind"] == "maturation_lease_acquired" for event in events["events"])

    ack = ack_worker_events(repo=str(tmp_path), worker_id="worker-01", event_ids=[events["events"][0]["event_id"]])
    assert ack["passed"] is True


def test_mcp_tools_happy_context_renew_and_abandon(tmp_path: Path) -> None:
    _write_registry(tmp_path, _registry(tmp_path, t1_ready=False, t2_ready=False))
    response = claim_next_maturation_slice(repo=str(tmp_path), worker_id="worker-01", campaign_id="camp:test")
    lease = response["lease"]

    context = get_slice_context(repo=str(tmp_path), lease_id=lease["lease_id"])
    assert context["feature"]["id"] == "feat:control.worker"
    renewed = renew_lease(
        repo=str(tmp_path),
        worker_id="worker-01",
        lease_id=lease["lease_id"],
        fencing_token=lease["fencing_token"],
    )
    assert renewed["lease"]["lease_id"] == lease["lease_id"]
    abandoned = abandon_slice(
        repo=str(tmp_path),
        worker_id="worker-01",
        lease_id=lease["lease_id"],
        fencing_token=lease["fencing_token"],
        reason="mcp happy path",
    )
    assert abandoned["lease"]["status"] == "abandoned"


def test_mcp_tools_surface_bad_sequences(tmp_path: Path) -> None:
    _write_registry(tmp_path, _registry(tmp_path, t1_ready=False, t2_ready=False))
    response = claim_next_maturation_slice(repo=str(tmp_path), worker_id="worker-01", campaign_id="camp:test")
    lease = response["lease"]

    with pytest.raises(ValueError, match="worker does not own lease"):
        renew_lease(repo=str(tmp_path), worker_id="worker-02", lease_id=lease["lease_id"], fencing_token=lease["fencing_token"])
    with pytest.raises(ValueError, match="stale fencing token"):
        abandon_slice(repo=str(tmp_path), worker_id="worker-01", lease_id=lease["lease_id"], fencing_token=999, reason="bad")

    failed = complete_slice(
        repo=str(tmp_path),
        worker_id="worker-01",
        lease_id=lease["lease_id"],
        fencing_token=lease["fencing_token"],
        result={
            "changed_paths": ["outside.py"],
            "tests_run": [{"command": "pytest", "exit_code": 1}],
            "evidence_paths": [],
            "requested_tier": "T1",
        },
    )
    assert failed["passed"] is False
    status = get_campaign_status(repo=str(tmp_path), campaign_id="camp:test")
    assert status["active_lease_count"] == 1
