from __future__ import annotations

from pathlib import Path
from typing import Any

from ssot_registry.control.paths import is_forbidden_path, path_is_under, normalize_repo_path
from ssot_registry.guards.claim_tier_gates import evaluate_claim_tier_gate
from ssot_registry.maturation.selector import build_registry_index


def evaluate_completion_guard(
    registry: dict[str, Any],
    lease: dict[str, Any],
    result: dict[str, Any],
    *,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    checks: dict[str, bool] = {}

    changed_paths = [normalize_repo_path(path) for path in result.get("changed_paths", []) if isinstance(path, str)]
    lease_roots = [normalize_repo_path(path) for path in lease.get("path_roots", [])]
    evidence_paths = [normalize_repo_path(path) for path in result.get("evidence_paths", []) if isinstance(path, str)]
    tests_run = [item for item in result.get("tests_run", []) if isinstance(item, dict)]

    checks["changed_paths_reported"] = bool(changed_paths)
    checks["changed_paths_under_lease"] = bool(changed_paths) and all(
        any(path_is_under(path, root) for root in lease_roots) for path in changed_paths
    )
    checks["no_forbidden_paths_changed"] = not any(is_forbidden_path(path) for path in changed_paths)
    checks["tests_passed"] = bool(tests_run) and all(int(test.get("exit_code", 1)) == 0 for test in tests_run)
    checks["evidence_paths_reported"] = bool(evidence_paths)

    root = Path(repo_root) if repo_root is not None else None
    if root is None:
        checks["evidence_paths_exist"] = bool(evidence_paths)
    else:
        checks["evidence_paths_exist"] = bool(evidence_paths) and all((root / path).exists() for path in evidence_paths)

    if not checks["changed_paths_reported"]:
        failures.append("completion requires changed_paths")
    if not checks["changed_paths_under_lease"]:
        failures.append("completion changed_paths must be under active lease roots")
    if not checks["no_forbidden_paths_changed"]:
        failures.append("completion changed_paths must not include forbidden paths")
    if not checks["tests_passed"]:
        failures.append("completion requires passing tests_run entries")
    if not checks["evidence_paths_reported"]:
        failures.append("completion requires evidence_paths")
    if not checks["evidence_paths_exist"]:
        failures.append("completion evidence_paths must exist")

    gate_result: dict[str, Any] | None = None
    requested_tier = result.get("requested_tier") or lease.get("to_tier")
    feature_id = str(lease.get("feature_id", ""))
    if isinstance(requested_tier, str) and feature_id:
        index = build_registry_index(registry)
        feature = index["features"].get(feature_id)
        claim_ids = feature.get("claim_ids", []) if feature else []
        candidate_claims = [
            index["claims"][claim_id]
            for claim_id in claim_ids
            if claim_id in index["claims"] and index["claims"][claim_id].get("tier") == requested_tier
        ]
        if candidate_claims:
            gate_results = [
                evaluate_claim_tier_gate(registry, claim, index, requested_tier=requested_tier, repo_root=root)
                for claim in candidate_claims
            ]
            gate_result = next((item for item in gate_results if item.get("passed")), gate_results[0])
            checks["tier_gate_passed"] = bool(gate_result.get("passed"))
            if not checks["tier_gate_passed"]:
                failures.extend(str(item) for item in gate_result.get("failures", []))
        else:
            checks["tier_gate_passed"] = False
            failures.append(f"no linked {requested_tier} claim found for feature {feature_id}")

    return {
        "passed": not failures,
        "failures": sorted(set(failures)),
        "warnings": warnings,
        "checks": checks,
        "gate_result": gate_result,
    }
