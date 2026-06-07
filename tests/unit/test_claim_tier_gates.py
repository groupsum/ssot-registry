from __future__ import annotations

from pathlib import Path

from ssot_registry.guards.claim_tier_gates import evaluate_claim_tier_gate


def _base_registry(tmp_path: Path, *, claim_tier: str = "T1", evidence_tier: str = "T1") -> dict[str, object]:
    test_path = tmp_path / "tests" / "test_gate.py"
    test_path.parent.mkdir(parents=True)
    test_path.write_text("def test_gate():\n    assert True\n", encoding="utf-8")
    evidence_path = tmp_path / ".ssot" / "evidence" / "gate.json"
    evidence_path.parent.mkdir(parents=True)
    evidence_path.write_text("{}", encoding="utf-8")
    return {
        "schema_version": "0.4.0",
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
                "id": "feat:gate",
                "title": "Gate feature",
                "description": "Gate test feature.",
                "implementation_status": "implemented",
                "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
                "plan": {"horizon": "current", "slot": None, "target_claim_tier": claim_tier, "target_lifecycle_stage": "active"},
                "requires": [],
                "spec_ids": [],
                "claim_ids": ["clm:gate"],
                "test_ids": ["tst:gate"],
            }
        ],
        "profiles": [],
        "tests": [
            {
                "id": "tst:gate",
                "title": "Gate test",
                "status": "passing",
                "kind": "pytest",
                "path": "tests/test_gate.py",
                "feature_ids": ["feat:gate"],
                "claim_ids": ["clm:gate"],
                "evidence_ids": ["evd:gate"],
            }
        ],
        "claims": [
            {
                "id": "clm:gate",
                "title": "Gate claim",
                "status": "asserted",
                "tier": claim_tier,
                "kind": "conformance",
                "description": "Gate claim.",
                "feature_ids": ["feat:gate"],
                "test_ids": ["tst:gate"],
                "evidence_ids": ["evd:gate"],
            }
        ],
        "evidence": [
            {
                "id": "evd:gate",
                "title": "Gate evidence",
                "status": "passed",
                "kind": "report",
                "tier": evidence_tier,
                "path": ".ssot/evidence/gate.json",
                "claim_ids": ["clm:gate"],
                "test_ids": ["tst:gate"],
            }
        ],
        "issues": [],
        "risks": [],
        "boundaries": [],
        "releases": [],
        "adrs": [],
        "specs": [],
    }


def _index(registry: dict[str, object]) -> dict[str, dict[str, dict[str, object]]]:
    return {
        "features": {row["id"]: row for row in registry["features"]},
        "profiles": {row["id"]: row for row in registry["profiles"]},
        "tests": {row["id"]: row for row in registry["tests"]},
        "claims": {row["id"]: row for row in registry["claims"]},
        "evidence": {row["id"]: row for row in registry["evidence"]},
        "issues": {row["id"]: row for row in registry["issues"]},
        "risks": {row["id"]: row for row in registry["risks"]},
        "boundaries": {row["id"]: row for row in registry["boundaries"]},
        "releases": {row["id"]: row for row in registry["releases"]},
    }


def test_t1_gate_accepts_passing_project_evidence(tmp_path: Path) -> None:
    registry = _base_registry(tmp_path, claim_tier="T1", evidence_tier="T1")
    result = evaluate_claim_tier_gate(registry, registry["claims"][0], _index(registry), repo_root=tmp_path)

    assert result["passed"] is True
    assert result["approved_tier"] == "T1"
    assert result["checks"]["t1_gate"] is True


def test_t1_gate_uses_evidence_owned_claim_and_test_links(tmp_path: Path) -> None:
    registry = _base_registry(tmp_path, claim_tier="T1", evidence_tier="T1")
    registry["claims"][0]["test_ids"] = []
    registry["claims"][0]["evidence_ids"] = []
    registry["tests"][0]["claim_ids"] = []

    result = evaluate_claim_tier_gate(registry, registry["claims"][0], _index(registry), repo_root=tmp_path)

    assert result["passed"] is True
    assert result["approved_tier"] == "T1"


def test_t2_gate_rejects_label_only_tier_inflation(tmp_path: Path) -> None:
    registry = _base_registry(tmp_path, claim_tier="T2", evidence_tier="T2")
    result = evaluate_claim_tier_gate(registry, registry["claims"][0], _index(registry), repo_root=tmp_path)

    assert result["passed"] is False
    assert result["approved_tier"] == "T1"
    assert any("robustness dimensions" in failure for failure in result["failures"])


def test_t2_gate_accepts_distinct_robustness_evidence(tmp_path: Path) -> None:
    registry = _base_registry(tmp_path, claim_tier="T2", evidence_tier="T2")
    evidence = registry["evidence"][0]
    evidence["robustness_dimensions"] = ["negative_cases", "edge_cases"]
    evidence["source_evidence_ids"] = ["evd:gate.t1"]

    result = evaluate_claim_tier_gate(registry, registry["claims"][0], _index(registry), repo_root=tmp_path)

    assert result["passed"] is True
    assert result["approved_tier"] == "T2"


def _add_t3_release_scope(registry: dict[str, object], *, include_evidence: bool = True) -> None:
    registry["evidence"][0]["tier"] = "T3"
    registry["evidence"][0]["robustness_dimensions"] = ["negative_cases", "cross_surface"]
    registry["evidence"][0]["source_evidence_ids"] = ["evd:gate.t1"]
    registry["evidence"][0]["release_context"] = {
        "release_id": "rel:test",
        "boundary_id": "bnd:test",
        "boundary_ids": ["bnd:test"],
    }
    registry["boundaries"] = [
        {
            "id": "bnd:test",
            "title": "Test boundary",
            "status": "frozen",
            "frozen": True,
            "feature_ids": ["feat:gate"],
            "profile_ids": [],
        }
    ]
    registry["releases"] = [
        {
            "id": "rel:test",
            "version": "0.1.0",
            "status": "candidate",
            "boundary_id": "bnd:test",
            "boundary_ids": ["bnd:test"],
            "claim_ids": ["clm:gate"],
            "evidence_ids": ["evd:gate"] if include_evidence else [],
        }
    ]


def test_t3_gate_accepts_certified_release_scope(tmp_path: Path) -> None:
    registry = _base_registry(tmp_path, claim_tier="T3", evidence_tier="T3")
    _add_t3_release_scope(registry)

    result = evaluate_claim_tier_gate(registry, registry["claims"][0], _index(registry), repo_root=tmp_path)

    assert result["passed"] is True
    assert result["approved_tier"] == "T3"
    assert result["checks"]["t3_release_context"] is True
    assert result["checks"]["t3_boundary_context"] is True
    assert result["checks"]["t3_release_certification_guard"] is True


def test_t3_gate_rejects_missing_release_context(tmp_path: Path) -> None:
    registry = _base_registry(tmp_path, claim_tier="T3", evidence_tier="T3")
    _add_t3_release_scope(registry)
    registry["evidence"][0]["release_context"].pop("release_id")

    result = evaluate_claim_tier_gate(registry, registry["claims"][0], _index(registry), repo_root=tmp_path)

    assert result["passed"] is False
    assert any("requires release context" in failure for failure in result["failures"])


def test_t3_gate_rejects_missing_boundary_context(tmp_path: Path) -> None:
    registry = _base_registry(tmp_path, claim_tier="T3", evidence_tier="T3")
    _add_t3_release_scope(registry)
    registry["evidence"][0]["release_context"].pop("boundary_id")
    registry["evidence"][0]["release_context"]["boundary_ids"] = []

    result = evaluate_claim_tier_gate(registry, registry["claims"][0], _index(registry), repo_root=tmp_path)

    assert result["passed"] is False
    assert any("requires boundary context" in failure for failure in result["failures"])


def test_t3_gate_rejects_release_without_explicit_evidence_coverage(tmp_path: Path) -> None:
    registry = _base_registry(tmp_path, claim_tier="T3", evidence_tier="T3")
    _add_t3_release_scope(registry, include_evidence=False)

    result = evaluate_claim_tier_gate(registry, registry["claims"][0], _index(registry), repo_root=tmp_path)

    assert result["passed"] is False
    assert any("has no evidence coverage for claim clm:gate" in failure for failure in result["failures"])


def test_t3_gate_rejects_release_blocking_issue_and_risk(tmp_path: Path) -> None:
    registry = _base_registry(tmp_path, claim_tier="T3", evidence_tier="T3")
    _add_t3_release_scope(registry)
    registry["issues"] = [
        {
            "id": "iss:blocker",
            "title": "Blocker",
            "status": "open",
            "severity": "high",
            "description": "Blocks release.",
            "plan": {"horizon": "current", "slot": None},
            "feature_ids": ["feat:gate"],
            "claim_ids": [],
            "test_ids": [],
            "evidence_ids": [],
            "risk_ids": [],
            "release_blocking": True,
        }
    ]
    registry["risks"] = [
        {
            "id": "rsk:blocker",
            "title": "Risk",
            "status": "active",
            "severity": "high",
            "description": "Blocks release.",
            "feature_ids": ["feat:gate"],
            "claim_ids": [],
            "test_ids": [],
            "evidence_ids": [],
            "issue_ids": [],
            "release_blocking": True,
        }
    ]

    result = evaluate_claim_tier_gate(registry, registry["claims"][0], _index(registry), repo_root=tmp_path)

    assert result["passed"] is False
    assert any("Release-blocking issue remains open" in failure for failure in result["failures"])
    assert any("Release-blocking risk remains active" in failure for failure in result["failures"])


def test_t4_evidence_contract_rejects_internal_self_attestation(tmp_path: Path) -> None:
    registry = _base_registry(tmp_path, claim_tier="T4", evidence_tier="T4")
    evidence = registry["evidence"][0]
    evidence.update(
        {
            "external_source": {
                "name": "Internal suite",
                "version": "1.0",
                "authorship_control": "internal",
            },
            "validation_mode": "external-authored-internal-run",
            "validation_scope": {"claim_ids": ["clm:gate"]},
            "result": "passed",
        }
    )

    result = evaluate_claim_tier_gate(
        registry,
        registry["claims"][0],
        _index(registry),
        repo_root=tmp_path,
        policy={"t4": {"require_t3": False}},
    )

    assert result["passed"] is False
    assert any("external validation authority" in failure for failure in result["failures"])
