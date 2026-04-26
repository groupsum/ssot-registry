from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from ssot_registry.api import create_entity, validate_registry

from .catalog import build_catalog_slice, resolve_selected_families


def _ids(rows: list[dict[str, object]]) -> set[str]:
    return {str(row["id"]) for row in rows}


def plan_scaffold(
    path: str | Path,
    *,
    profiles: list[str] | None = None,
    include_claims: bool = False,
    include_evidence: bool = False,
) -> dict[str, object]:
    registry_report = validate_registry(path)
    if not registry_report["passed"]:
        raise ValueError("Target registry must validate before conformance scaffold planning")

    catalog = build_catalog_slice(profiles)
    registry_path = Path(path) / ".ssot" / "registry.json" if Path(path).is_dir() else Path(path)
    repo_root = registry_path.parent.parent if registry_path.name == "registry.json" else Path(path)
    import json

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    existing = {section: _ids(registry.get(section, [])) for section in ("features", "claims", "tests", "evidence")}

    missing = {
        "features": [row["id"] for row in catalog["features"] if row["id"] not in existing["features"]],
        "claims": [row["id"] for row in catalog["claims"] if row["id"] not in existing["claims"]],
        "tests": [row["id"] for row in catalog["tests"] if row["id"] not in existing["tests"]],
        "evidence": [row["id"] for row in catalog["evidence"] if row["id"] not in existing["evidence"]],
    }

    planned_feature_ids = set(existing["features"]) | set(missing["features"])
    planned_claim_ids = set(existing["claims"]) | (set(missing["claims"]) if include_claims else set())
    planned_evidence_ids = set(existing["evidence"]) | (set(missing["evidence"]) if include_evidence else set())

    blocked_tests: list[dict[str, object]] = []
    creatable_tests: list[str] = []
    for row in catalog["tests"]:
        test_id = str(row["id"])
        if test_id in existing["tests"]:
            continue
        reasons: list[str] = []
        for feature_id in row["feature_ids"]:
            if feature_id not in planned_feature_ids:
                reasons.append(f"missing feature {feature_id}")
        for claim_id in row["claim_ids"]:
            if claim_id not in planned_claim_ids:
                reasons.append(f"missing claim {claim_id}")
        for evidence_id in row["evidence_ids"]:
            if evidence_id not in planned_evidence_ids:
                reasons.append(f"missing evidence {evidence_id}")
        if reasons:
            blocked_tests.append({"id": test_id, "reasons": reasons})
        else:
            creatable_tests.append(test_id)

    return {
        "passed": True,
        "repo_root": repo_root.as_posix(),
        "profiles": catalog["profiles"],
        "families": resolve_selected_families(profiles),
        "missing": missing,
        "creatable_test_ids": creatable_tests,
        "blocked_tests": blocked_tests,
        "include_claims": include_claims,
        "include_evidence": include_evidence,
    }


def apply_scaffold(
    path: str | Path,
    *,
    profiles: list[str] | None = None,
    include_claims: bool = False,
    include_evidence: bool = False,
) -> dict[str, object]:
    plan = plan_scaffold(path, profiles=profiles, include_claims=include_claims, include_evidence=include_evidence)
    catalog = build_catalog_slice(profiles)
    repo_root = Path(plan["repo_root"])

    created = {"features": [], "claims": [], "tests": [], "evidence": []}
    unchanged = {"features": [], "claims": [], "tests": [], "evidence": []}

    missing = {key: set(value) for key, value in plan["missing"].items()}
    creatable_tests = set(plan["creatable_test_ids"])

    claim_rows = {row["id"]: row for row in catalog["claims"]}
    evidence_rows = {row["id"]: row for row in catalog["evidence"]}
    feature_rows = {row["id"]: row for row in catalog["features"]}
    test_rows = {row["id"]: row for row in catalog["tests"]}

    for feature_id in missing["features"]:
        row = deepcopy(feature_rows[feature_id])
        row["spec_ids"] = []
        row["claim_ids"] = []
        row["test_ids"] = []
        create_entity(path, "features", row)
        created["features"].append(feature_id)

    if include_claims:
        for claim_id in missing["claims"]:
            row = deepcopy(claim_rows[claim_id])
            row["test_ids"] = []
            row["evidence_ids"] = []
            create_entity(path, "claims", row)
            created["claims"].append(claim_id)
    else:
        unchanged["claims"].extend(sorted(plan["missing"]["claims"]))

    if include_evidence:
        for evidence_id in missing["evidence"]:
            row = deepcopy(evidence_rows[evidence_id])
            target = repo_root / str(row["path"])
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_text("{}", encoding="utf-8")
            row["test_ids"] = []
            create_entity(path, "evidence", row)
            created["evidence"].append(evidence_id)

    for test_id in creatable_tests:
        if test_id not in missing["tests"]:
            continue
        row = deepcopy(test_rows[test_id])
        target = repo_root / str(row["path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")
        create_entity(path, "tests", row)
        created["tests"].append(test_id)

    validation = validate_registry(path)
    return {
        "passed": validation["passed"],
        "profiles": plan["profiles"],
        "families": plan["families"],
        "created": created,
        "unchanged": unchanged,
        "blocked_tests": plan["blocked_tests"],
        "validation": validation,
    }
