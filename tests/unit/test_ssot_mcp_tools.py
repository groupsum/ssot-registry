from __future__ import annotations

from pathlib import Path

from ssot_mcp.tools import claim_next_maturation_slice, get_worker_events

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
