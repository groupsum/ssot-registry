from __future__ import annotations

from pathlib import Path

from ssot_registry.control.service import ControlPlane
from tests.unit.test_worker_control_plane import _registry_missing_target_claim, _write_registry


def test_post_repair_claim_next_grants_a_lease_after_direct_scaffold(tmp_path: Path) -> None:
    _write_registry(tmp_path, _registry_missing_target_claim(tmp_path))
    plane = ControlPlane(tmp_path)

    blocked = plane.claim_next_maturation_slice(
        worker_id="worker-01",
        campaign_id="camp:test",
        target_tier="T2",
        auto_scaffold=False,
    )
    assert blocked["kind"] == "blocked"

    scaffold = plane.scaffold_target_claim_wiring(
        feature_id="feat:control.missing-wiring",
        target_tier="T1",
    )
    assert scaffold["passed"] is True

    retry = plane.claim_next_maturation_slice(
        worker_id="worker-02",
        campaign_id="camp:test",
        target_tier="T2",
    )
    assert retry["kind"] == "lease_granted"
