from __future__ import annotations

from pathlib import Path

import pytest

from ssot_registry.control.paths import ensure_allowed_path, path_overlaps
from ssot_registry.control.service import ControlPlane
from ssot_registry.control.sqlite_store import ControlStore
from ssot_registry.maturation.selector import next_maturation_slice
from ssot_registry.util.jsonio import stable_json_dumps


def _write_registry(repo: Path, registry: dict[str, object]) -> None:
    path = repo / ".ssot" / "registry.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(stable_json_dumps(registry), encoding="utf-8")


def _registry(tmp_path: Path, *, t1_ready: bool = False, t2_ready: bool = False) -> dict[str, object]:
    test_path = tmp_path / "tests" / "control" / "test_worker.py"
    test_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.write_text("def test_worker():\n    assert True\n", encoding="utf-8")
    evidence_root = tmp_path / ".ssot" / "evidence" / "control" / "worker"
    evidence_root.mkdir(parents=True, exist_ok=True)
    (evidence_root / "t1.json").write_text("{}", encoding="utf-8")
    (evidence_root / "t2.json").write_text("{}", encoding="utf-8")
    t1_evidence = ["evd:control.worker.t1"] if t1_ready else []
    t2_evidence = ["evd:control.worker.t2"] if t2_ready else []
    return {
        "schema_version": "0.7.0",
        "repo": {"id": "repo:test", "name": "test", "version": "0.1.0", "kind": "repo-local"},
        "tooling": {"ssot_registry_version": "0.0.0", "initialized_with_version": "0.0.0", "last_upgraded_from_version": "0.0.0"},
        "paths": {
            "ssot_root": ".ssot",
            "schema_root": ".ssot/schemas",
            "adr_root": ".ssot/adr",
            "spec_root": ".ssot/specs",
            "graph_root": ".ssot/graphs",
            "evidence_root": ".ssot/evidence",
            "release_root": ".ssot/releases",
            "report_root": ".ssot/reports",
            "cache_root": ".ssot/cache",
        },
        "program": {"active_boundary_id": "bnd:test", "active_release_id": "rel:test"},
        "guard_policies": {},
        "document_id_reservations": {"adr": [], "spec": []},
        "features": [
            {
                "id": "feat:control.worker",
                "title": "Worker control",
                "description": "Worker control test feature.",
                "implementation_status": "partial",
                "origin": "repo-local",
                "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
                "plan": {"horizon": "current", "slot": None, "target_claim_tier": "T2", "target_lifecycle_stage": "active"},
                "requires": [],
                "spec_ids": [],
                "claim_ids": ["clm:control.worker.t0", "clm:control.worker.t1", "clm:control.worker.t2"],
                "test_ids": ["tst:control.worker"],
                "parent_feature_ids": [],
                "lease_roots": ["tests/control", ".ssot/evidence/control/worker"],
            }
        ],
        "profiles": [],
        "tests": [
            {
                "id": "tst:control.worker",
                "title": "Worker control test",
                "status": "passing",
                "kind": "pytest",
                "path": "tests/control/test_worker.py",
                "origin": "repo-local",
                "feature_ids": ["feat:control.worker"],
                "claim_ids": ["clm:control.worker.t1", "clm:control.worker.t2"],
                "evidence_ids": ["evd:control.worker.t1", "evd:control.worker.t2"],
            }
        ],
        "claims": [
            {
                "id": "clm:control.worker.t0",
                "title": "Worker declared",
                "status": "declared",
                "tier": "T0",
                "kind": "runtime",
                "description": "Worker control is tracked.",
                "origin": "repo-local",
                "feature_ids": ["feat:control.worker"],
                "test_ids": [],
                "evidence_ids": [],
                "depends_on_claim_ids": [],
            },
            {
                "id": "clm:control.worker.t1",
                "title": "Worker direct verification",
                "status": "asserted",
                "tier": "T1",
                "kind": "runtime",
                "description": "Worker control direct behavior is verified.",
                "origin": "repo-local",
                "feature_ids": ["feat:control.worker"],
                "test_ids": ["tst:control.worker"],
                "evidence_ids": t1_evidence,
                "depends_on_claim_ids": ["clm:control.worker.t0"],
            },
            {
                "id": "clm:control.worker.t2",
                "title": "Worker robustness verification",
                "status": "asserted",
                "tier": "T2",
                "kind": "runtime",
                "description": "Worker control robustness is verified.",
                "origin": "repo-local",
                "feature_ids": ["feat:control.worker"],
                "test_ids": ["tst:control.worker"],
                "evidence_ids": t2_evidence,
                "depends_on_claim_ids": ["clm:control.worker.t1"],
            },
        ],
        "evidence": [
            {
                "id": "evd:control.worker.t1",
                "title": "Worker T1 evidence",
                "status": "passed",
                "kind": "pytest",
                "tier": "T1",
                "origin": "repo-local",
                "path": ".ssot/evidence/control/worker/t1.json",
                "claim_ids": ["clm:control.worker.t1"],
                "test_ids": ["tst:control.worker"],
            },
            {
                "id": "evd:control.worker.t2",
                "title": "Worker T2 evidence",
                "status": "passed",
                "kind": "pytest",
                "tier": "T2",
                "origin": "repo-local",
                "path": ".ssot/evidence/control/worker/t2.json",
                "claim_ids": ["clm:control.worker.t2"],
                "test_ids": ["tst:control.worker"],
                "robustness_dimensions": ["negative_cases", "concurrency"],
                "source_evidence_ids": ["evd:control.worker.t1"],
            },
        ],
        "issues": [],
        "risks": [],
        "boundaries": [],
        "releases": [],
        "adrs": [],
        "specs": [],
    }


def test_path_roots_reject_forbidden_and_detect_overlap() -> None:
    assert ensure_allowed_path("src/a/**") == "src/a"
    assert path_overlaps("src/a", "src/a/file.py")
    with pytest.raises(ValueError, match="forbidden"):
        ensure_allowed_path(".ssot/registry.json")


def test_sqlite_store_enforces_single_active_transition(tmp_path: Path) -> None:
    store = ControlStore(tmp_path)
    store.register_worker("worker-01", os_user="worker01")
    store.ensure_campaign("camp:test", "T2")
    first = store.create_maturation_lease(
        campaign_id="camp:test",
        worker_id="worker-01",
        feature_id="feat:a",
        from_tier="T0",
        to_tier="T1",
        path_roots=["src/a"],
        registry_hash_at_claim="hash",
        expires_at="2999-01-01T00:00:00Z",
    )
    store.activate_lease(first["lease_id"])
    with pytest.raises(ValueError, match="path lease conflict"):
        store.create_maturation_lease(
            campaign_id="camp:test",
            worker_id="worker-01",
            feature_id="feat:b",
            from_tier="T0",
            to_tier="T1",
            path_roots=["src/a/file.py"],
            registry_hash_at_claim="hash",
            expires_at="2999-01-01T00:00:00Z",
        )
    renewed = store.renew_lease(first["lease_id"], "worker-01", first["fencing_token"], "2999-01-02T00:00:00Z")
    assert renewed["expires_at"] == "2999-01-02T00:00:00Z"
    with pytest.raises(ValueError, match="stale fencing token"):
        store.renew_lease(first["lease_id"], "worker-01", 999, "2999-01-03T00:00:00Z")


def test_maturation_selector_moves_t0_to_t1_then_t1_to_t2(tmp_path: Path) -> None:
    registry = _registry(tmp_path, t1_ready=False, t2_ready=False)
    assert next_maturation_slice(registry, repo_root=tmp_path)["to_tier"] == "T1"

    registry = _registry(tmp_path, t1_ready=True, t2_ready=False)
    assert next_maturation_slice(registry, repo_root=tmp_path)["to_tier"] == "T2"

    registry = _registry(tmp_path, t1_ready=True, t2_ready=True)
    assert next_maturation_slice(registry, repo_root=tmp_path) is None


def test_control_plane_claim_renew_and_abandon_slice(tmp_path: Path) -> None:
    _write_registry(tmp_path, _registry(tmp_path, t1_ready=False, t2_ready=False))
    plane = ControlPlane(tmp_path)
    response = plane.claim_next_maturation_slice(worker_id="worker-01", campaign_id="camp:test")

    assert response["kind"] == "lease_granted"
    lease = response["lease"]
    assert lease["to_tier"] == "T1"
    assert "tests/control" in lease["path_roots"]

    renewed = plane.renew_lease(worker_id="worker-01", lease_id=lease["lease_id"], fencing_token=lease["fencing_token"])
    assert renewed["lease"]["lease_id"] == lease["lease_id"]

    abandoned = plane.abandon_slice(
        worker_id="worker-01",
        lease_id=lease["lease_id"],
        fencing_token=lease["fencing_token"],
        reason="unit test",
    )
    assert abandoned["lease"]["status"] == "abandoned"
    events = plane.get_worker_events(worker_id="worker-01", after_event_id=0)["events"]
    assert {event["kind"] for event in events} >= {"maturation_lease_acquired", "maturation_lease_abandoned"}
