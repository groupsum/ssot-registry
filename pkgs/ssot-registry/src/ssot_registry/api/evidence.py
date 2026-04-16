from __future__ import annotations

from pathlib import Path

from ssot_registry.model.enums import CLAIM_TIER_RANK
from ssot_registry.validators.identity import build_index
from .load import load_registry


def verify_evidence_rows(path: str | Path, evidence_id: str | None = None) -> dict[str, object]:
    registry_path, repo_root, registry = load_registry(path)
    failures: list[str] = []
    index = build_index(registry, failures)

    if evidence_id is not None and evidence_id not in index["evidence"]:
        return {
            "passed": False,
            "registry_path": registry_path.as_posix(),
            "failures": failures + [f"Missing evidence {evidence_id}"],
            "evidence": [],
        }

    selected = (
        [index["evidence"][evidence_id]]
        if evidence_id is not None
        else [index["evidence"][entity_id] for entity_id in sorted(index["evidence"])]
    )

    reports: list[dict[str, object]] = []
    for evidence in selected:
        local_failures: list[str] = []
        path_value = evidence["path"]
        if not (repo_root / path_value).exists():
            local_failures.append(f"Evidence path does not exist: {path_value}")
        if evidence["status"] != "passed":
            local_failures.append(f"Evidence {evidence['id']} status is {evidence['status']}, expected passed")
        for test_id in evidence.get("test_ids", []):
            test = index["tests"].get(test_id)
            if test is None or test.get("status") != "passing":
                local_failures.append(f"Evidence {evidence['id']} linked test is not passing: {test_id}")
        for claim_id in evidence.get("claim_ids", []):
            claim = index["claims"].get(claim_id)
            if claim is None:
                local_failures.append(f"Evidence {evidence['id']} references missing claim {claim_id}")
                continue
            if CLAIM_TIER_RANK[evidence["tier"]] < CLAIM_TIER_RANK[claim["tier"]]:
                local_failures.append(
                    f"Evidence {evidence['id']} tier {evidence['tier']} is below linked claim tier {claim['tier']} on {claim_id}"
                )
        reports.append(
            {
                "evidence_id": evidence["id"],
                "passed": not local_failures,
                "failures": local_failures,
            }
        )

    all_failures = failures + [failure for report in reports for failure in report["failures"]]
    return {
        "passed": not all_failures,
        "registry_path": registry_path.as_posix(),
        "failures": sorted(set(all_failures)),
        "evidence": reports,
    }
