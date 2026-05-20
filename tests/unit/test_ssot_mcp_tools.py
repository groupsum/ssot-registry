from __future__ import annotations

from pathlib import Path

import pytest

from ssot_mcp.tools import (
    abandon_slice,
    ack_worker_events,
    claim_next_maturation_slice,
    configure_repo,
    complete_slice,
    get_campaign_status,
    get_slice_context,
    get_worker_events,
    get_blocked_transitions,
    registry_entity_delete,
    registry_entity_get,
    registry_entity_link,
    registry_entity_list,
    registry_entity_search,
    registry_entity_unlink,
    registry_entity_upsert,
    repair_blocked_transition,
    run_ssot_cli,
    scaffold_target_claim_wiring,
    renew_lease,
)
from tests.helpers import temp_repo_from_fixture

from .test_worker_control_plane import _registry, _registry_missing_target_claim, _write_registry


def test_mcp_tools_delegate_to_control_plane(tmp_path: Path) -> None:
    configure_repo(None)
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
    configure_repo(None)
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
    configure_repo(None)
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


def test_mcp_tools_can_use_pinned_repo_without_repo_argument(tmp_path: Path) -> None:
    try:
        _write_registry(tmp_path, _registry(tmp_path, t1_ready=False, t2_ready=False))
        configure_repo(tmp_path)

        response = claim_next_maturation_slice(worker_id="worker-01", campaign_id="camp:test")

        assert response["kind"] == "lease_granted"
        events = get_worker_events(worker_id="worker-01", campaign_id="camp:test")
        assert any(event["kind"] == "maturation_lease_acquired" for event in events["events"])
    finally:
        configure_repo(None)


def test_mcp_tools_reject_repo_outside_pinned_root(tmp_path: Path) -> None:
    other = tmp_path / "other"
    other.mkdir()
    try:
        configure_repo(tmp_path)
        with pytest.raises(ValueError, match="pinned"):
            get_campaign_status(repo=str(other), campaign_id="camp:test")
    finally:
        configure_repo(None)


def test_mcp_registry_entity_tools_list_search_get_and_upsert(tmp_path: Path) -> None:
    configure_repo(None)
    temp_dir = temp_repo_from_fixture("repo_valid")
    repo = Path(temp_dir.name) / "repo"

    listed = registry_entity_list(repo=str(repo), section="feature")
    assert listed["total"] == 1
    searched = registry_entity_search(repo=str(repo), section="features", query="connection")
    assert searched["entities"][0]["id"] == "feat:rfc.9000.connection-migration"
    fetched = registry_entity_get(repo=str(repo), section="features", entity_id="feat:rfc.9000.connection-migration")
    assert fetched["entity"]["title"] == "RFC 9000 connection migration"

    updated = registry_entity_upsert(
        repo=str(repo),
        section="features",
        entity={
            **fetched["entity"],
            "description": "Updated through ssot-mcp.",
        },
    )

    assert updated["passed"] is True
    assert updated["entity"]["description"] == "Updated through ssot-mcp."
    events = get_worker_events(repo=str(repo))
    assert events["events"][-1]["kind"] == "registry_updated"
    temp_dir.cleanup()


def test_mcp_registry_entity_tools_create_link_unlink_and_delete(tmp_path: Path) -> None:
    configure_repo(None)
    temp_dir = temp_repo_from_fixture("repo_valid")
    repo = Path(temp_dir.name) / "repo"

    created = registry_entity_upsert(
        repo=str(repo),
        section="issues",
        entity={
            "id": "iss:mcp.extra",
            "title": "Extra issue",
            "status": "open",
            "severity": "low",
            "description": "Extra issue created through ssot-mcp.",
            "body": None,
            "release_blocking": False,
            "plan": {"horizon": "backlog", "slot": None},
            "origin": "repo-local",
            "feature_ids": [],
            "claim_ids": [],
            "test_ids": [],
            "evidence_ids": [],
            "risk_ids": [],
        },
    )
    assert created["passed"] is True

    linked = registry_entity_link(
        repo=str(repo),
        section="issues",
        entity_id="iss:mcp.extra",
        links={"feature_ids": ["feat:rfc.9000.connection-migration"]},
    )
    assert "feat:rfc.9000.connection-migration" in linked["entity"]["feature_ids"]

    unlinked = registry_entity_unlink(
        repo=str(repo),
        section="issues",
        entity_id="iss:mcp.extra",
        links={"feature_ids": ["feat:rfc.9000.connection-migration"]},
    )
    assert "feat:rfc.9000.connection-migration" not in unlinked["entity"]["feature_ids"]
    deleted = registry_entity_delete(repo=str(repo), section="issues", entity_id="iss:mcp.extra")
    assert deleted["passed"] is True
    temp_dir.cleanup()


def test_mcp_run_ssot_cli_executes_against_resolved_repo(tmp_path: Path) -> None:
    configure_repo(None)
    temp_dir = temp_repo_from_fixture("repo_valid")
    repo = Path(temp_dir.name) / "repo"

    result = run_ssot_cli(repo=str(repo), args=["validate", "."])

    assert result["passed"] is True
    assert result["exit_code"] == 0
    assert result["output"]["passed"] is True
    temp_dir.cleanup()


def test_mcp_repair_queue_tools_scaffold_and_resolve(tmp_path: Path) -> None:
    configure_repo(None)
    _write_registry(tmp_path, _registry_missing_target_claim(tmp_path))
    blocked = claim_next_maturation_slice(
        repo=str(tmp_path),
        worker_id="worker-01",
        campaign_id="camp:test",
        target_tier="T2",
        auto_scaffold=False,
    )
    assert blocked["kind"] == "blocked"
    assert blocked["reason"] == "missing_target_tier_claim_wiring"
    assert blocked["problem_detail"]["blockers"][0]["feature_id"] == "feat:control.missing-wiring"
    assert any(item["tool"] == "repair_blocked_transition" for item in blocked["problem_detail"]["recommendations"])
    blocked_id = blocked["blocked_transitions"][0]["blocked_id"]

    listed = get_blocked_transitions(repo=str(tmp_path), campaign_id="camp:test")
    assert listed["blocked_transitions"][0]["blocked_id"] == blocked_id
    repaired = repair_blocked_transition(repo=str(tmp_path), blocked_id=blocked_id)

    assert repaired["passed"] is True
    scaffold = scaffold_target_claim_wiring(repo=str(tmp_path), feature_id="feat:control.missing-wiring", target_tier="T1")
    assert scaffold["passed"] is True
