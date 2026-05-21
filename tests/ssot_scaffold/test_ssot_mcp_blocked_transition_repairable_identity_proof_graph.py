from __future__ import annotations

from pathlib import Path

from ssot_registry.control.service import ControlPlane
from tests.unit.test_worker_control_plane import _registry_missing_target_claim, _write_registry


def test_repair_blocked_transition_returns_resolved_blocker_identity(tmp_path: Path) -> None:
    _write_registry(tmp_path, _registry_missing_target_claim(tmp_path))
    plane = ControlPlane(tmp_path)

    blocked = plane.claim_next_maturation_slice(
        worker_id="worker-01",
        campaign_id="camp:test",
        target_tier="T2",
        auto_scaffold=False,
    )
    blocked_id = blocked["blocked_transitions"][0]["blocked_id"]

    scaffold = plane.scaffold_target_claim_wiring(
        feature_id="feat:control.missing-wiring",
        target_tier="T1",
    )
    assert scaffold["passed"] is True

    repaired = plane.repair_blocked_transition(blocked_id=blocked_id)
    assert repaired["passed"] is True
    assert repaired["already_resolved"] is True
    assert repaired["blocked_transition"]["blocked_id"] == blocked_id
    assert repaired["blocked_transition"]["status"] == "resolved"
