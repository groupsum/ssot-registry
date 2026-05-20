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
    with pytest.raises(ValueError, match="forbidden"):
        ensure_allowed_path(".git/index")
    with pytest.raises(ValueError, match="path escapes"):
        ensure_allowed_path("../outside")
    with pytest.raises(ValueError, match="repository root"):
        ensure_allowed_path("")


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


def test_sqlite_store_rejects_duplicate_os_user_and_open_transition(tmp_path: Path) -> None:
    store = ControlStore(tmp_path)
    store.register_worker("worker-01", os_user="worker")
    with pytest.raises(Exception):
        store.register_worker("worker-02", os_user="worker")

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
    with pytest.raises(Exception):
        store.create_maturation_lease(
            campaign_id="camp:test",
            worker_id="worker-01",
            feature_id="feat:a",
            from_tier="T0",
            to_tier="T1",
            path_roots=["tests/a"],
            registry_hash_at_claim="hash",
            expires_at="2999-01-01T00:00:00Z",
        )


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

    acked = plane.ack_worker_events(worker_id="worker-01", event_ids=[event["event_id"] for event in events], action="tested")
    assert acked["passed"] is True
    assert plane.get_worker_events(worker_id="worker-01", after_event_id=events[-1]["event_id"])["events"] == []


def test_control_plane_complete_slice_happy_path_records_gate_and_events(tmp_path: Path) -> None:
    _write_registry(tmp_path, _registry(tmp_path, t1_ready=True, t2_ready=False))
    plane = ControlPlane(tmp_path)
    plane.store.register_worker("worker-01", os_user="worker01")
    plane.store.ensure_campaign("camp:test", "T2")
    lease = plane.store.create_maturation_lease(
        campaign_id="camp:test",
        worker_id="worker-01",
        feature_id="feat:control.worker",
        from_tier="T0",
        to_tier="T1",
        path_roots=["tests/control", ".ssot/evidence/control/worker"],
        registry_hash_at_claim="hash",
        expires_at="2999-01-01T00:00:00Z",
    )
    lease = plane.store.activate_lease(lease["lease_id"])

    completed = plane.complete_slice(
        worker_id="worker-01",
        lease_id=lease["lease_id"],
        fencing_token=lease["fencing_token"],
        result={
            "changed_paths": ["tests/control/test_worker.py", ".ssot/evidence/control/worker/t1.json"],
            "tests_run": [{"command": "python -m pytest tests/control/test_worker.py -q", "exit_code": 0}],
            "evidence_paths": [".ssot/evidence/control/worker/t1.json"],
            "requested_tier": "T1",
        },
    )

    assert completed["passed"] is True
    assert completed["lease"]["status"] == "done"
    assert completed["completion"]["checks"]["tier_gate_passed"] is True
    events = plane.get_worker_events(worker_id="worker-01")["events"]
    assert [event["kind"] for event in events[-2:]] == ["tier_gate_passed", "maturation_lease_completed"]
    with plane.store.connect() as conn:
        reports = conn.execute("SELECT requested_tier, approved_tier, passed FROM tier_gate_reports").fetchall()
    assert [(row["requested_tier"], row["approved_tier"], row["passed"]) for row in reports] == [("T1", "T1", 1)]


def test_control_plane_completion_failure_keeps_lease_active_and_emits_failure(tmp_path: Path) -> None:
    _write_registry(tmp_path, _registry(tmp_path, t1_ready=False, t2_ready=False))
    plane = ControlPlane(tmp_path)
    plane.store.register_worker("worker-01", os_user="worker01")
    plane.store.ensure_campaign("camp:test", "T2")
    lease = plane.store.create_maturation_lease(
        campaign_id="camp:test",
        worker_id="worker-01",
        feature_id="feat:control.worker",
        from_tier="T0",
        to_tier="T1",
        path_roots=["tests/control", ".ssot/evidence/control/worker"],
        registry_hash_at_claim="hash",
        expires_at="2999-01-01T00:00:00Z",
    )
    lease = plane.store.activate_lease(lease["lease_id"])

    failed = plane.complete_slice(
        worker_id="worker-01",
        lease_id=lease["lease_id"],
        fencing_token=lease["fencing_token"],
        result={
            "changed_paths": ["tests/control/test_worker.py"],
            "tests_run": [{"command": "python -m pytest tests/control/test_worker.py -q", "exit_code": 1}],
            "evidence_paths": [".ssot/evidence/control/worker/t1.json"],
            "requested_tier": "T1",
        },
    )

    assert failed["passed"] is False
    assert plane.store.get_lease(lease["lease_id"])["status"] == "active"
    assert "completion requires passing tests_run entries" in failed["completion"]["failures"]
    events = plane.get_worker_events(worker_id="worker-01")["events"]
    assert events[-1]["kind"] == "tier_gate_failed"


def test_control_plane_rejects_bad_sequences_and_expired_leases(tmp_path: Path) -> None:
    _write_registry(tmp_path, _registry(tmp_path, t1_ready=True, t2_ready=False))
    plane = ControlPlane(tmp_path)
    plane.store.register_worker("worker-01", os_user="worker01")
    plane.store.ensure_campaign("camp:test", "T2")
    lease = plane.store.create_maturation_lease(
        campaign_id="camp:test",
        worker_id="worker-01",
        feature_id="feat:control.worker",
        from_tier="T0",
        to_tier="T1",
        path_roots=["tests/control"],
        registry_hash_at_claim="hash",
        expires_at="2000-01-01T00:00:00Z",
    )
    lease = plane.store.activate_lease(lease["lease_id"])

    with pytest.raises(ValueError, match="worker does not own lease"):
        plane.renew_lease(worker_id="worker-02", lease_id=lease["lease_id"], fencing_token=lease["fencing_token"])
    with pytest.raises(ValueError, match="stale fencing token"):
        plane.abandon_slice(worker_id="worker-01", lease_id=lease["lease_id"], fencing_token=99, reason="bad token")

    expired = plane.expire_due_leases()
    assert expired["expired"][0]["status"] == "expired"
    with pytest.raises(ValueError, match="lease is not active: expired"):
        plane.complete_slice(
            worker_id="worker-01",
            lease_id=lease["lease_id"],
            fencing_token=lease["fencing_token"],
            result={"changed_paths": ["tests/control/test_worker.py"], "tests_run": [], "evidence_paths": [], "requested_tier": "T1"},
        )
    assert plane.get_worker_events(worker_id="worker-01")["events"][-1]["kind"] == "lease_expired"


def test_control_plane_returns_campaign_complete_when_target_already_met(tmp_path: Path) -> None:
    _write_registry(tmp_path, _registry(tmp_path, t1_ready=True, t2_ready=True))
    plane = ControlPlane(tmp_path)

    response = plane.claim_next_maturation_slice(worker_id="worker-01", campaign_id="camp:test", target_tier="T2")

    assert response["kind"] == "campaign_complete"
    assert response["campaign"]["complete"] is True
