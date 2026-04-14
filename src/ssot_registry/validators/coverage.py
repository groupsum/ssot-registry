from __future__ import annotations

from ssot_registry.guards.feature_requirements import evaluate_required_feature_failures


IN_SCOPE_HORIZONS = {"current", "explicit"}
TARGETED_OR_IMPLEMENTED_HORIZONS = {"current", "explicit", "next", "future"}


def validate_coverage(index: dict[str, dict[str, dict[str, object]]], failures: list[str], warnings: list[str]) -> None:
    for feature_id, row in index["features"].items():
        horizon = row.get("plan", {}).get("horizon")
        if row.get("implementation_status") == "implemented":
            if not row.get("claim_ids"):
                failures.append(f"features.{feature_id} is implemented but has no linked claims")
            if not row.get("test_ids"):
                failures.append(f"features.{feature_id} is implemented but has no linked tests")
        if horizon in IN_SCOPE_HORIZONS:
            if not row.get("claim_ids"):
                failures.append(f"features.{feature_id} is in-bound but has no linked claims")
            if not row.get("test_ids"):
                failures.append(f"features.{feature_id} is in-bound but has no linked tests")

        requirement_failures = evaluate_required_feature_failures(feature_id, index)
        if requirement_failures:
            cycle_failures = [failure for failure in requirement_failures if "cycle detected" in failure.lower()]
            non_cycle_failures = [failure for failure in requirement_failures if failure not in cycle_failures]
            failures.extend(cycle_failures)
            if non_cycle_failures:
                if row.get("implementation_status") == "implemented" or horizon in TARGETED_OR_IMPLEMENTED_HORIZONS:
                    failures.extend(non_cycle_failures)
                else:
                    warnings.extend(non_cycle_failures)

    for test_id, row in index["tests"].items():
        if not row.get("feature_ids"):
            warnings.append(f"tests.{test_id} has no linked features")
        if not row.get("claim_ids"):
            failures.append(f"tests.{test_id} has no linked claims")
        if not row.get("evidence_ids"):
            failures.append(f"tests.{test_id} has no linked evidence rows")

    for claim_id, row in index["claims"].items():
        if not row.get("feature_ids"):
            warnings.append(f"claims.{claim_id} has no linked features")
        if not row.get("test_ids"):
            warnings.append(f"claims.{claim_id} has no linked tests")
        if not row.get("evidence_ids"):
            warnings.append(f"claims.{claim_id} has no linked evidence")

    for release_id, release in index["releases"].items():
        boundary = index["boundaries"].get(release.get("boundary_id"))
        if boundary is None:
            continue
        for feature_id in boundary.get("feature_ids", []):
            if not any(
                claim_id in index["claims"] and feature_id in index["claims"][claim_id].get("feature_ids", [])
                for claim_id in release.get("claim_ids", [])
            ):
                failures.append(f"releases.{release_id} has no claim coverage for boundary feature {feature_id}")
