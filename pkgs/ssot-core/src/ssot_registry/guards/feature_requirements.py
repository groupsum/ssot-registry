from __future__ import annotations

from typing import Any


def _feature_direct_proof_failures(feature: dict[str, Any], index: dict[str, dict[str, dict[str, Any]]]) -> list[str]:
    failures: list[str] = []
    feature_id = feature["id"]
    if feature.get("implementation_status") != "implemented":
        failures.append(f"Required feature {feature_id} is not implemented")

    linked_tests = [index["tests"][test_id] for test_id in feature.get("test_ids", []) if test_id in index["tests"]]
    if not linked_tests:
        failures.append(f"Required feature {feature_id} has no linked tests")
    elif not all(test.get("status") == "passing" for test in linked_tests):
        failures.append(f"Required feature {feature_id} has non-passing linked tests")

    evidence_ids: set[str] = set()
    for test in linked_tests:
        evidence_ids.update(test.get("evidence_ids", []))
    for claim_id in feature.get("claim_ids", []):
        claim = index["claims"].get(claim_id)
        if claim is not None:
            evidence_ids.update(claim.get("evidence_ids", []))
    linked_evidence = [index["evidence"][evidence_id] for evidence_id in evidence_ids if evidence_id in index["evidence"]]
    if not linked_evidence:
        failures.append(f"Required feature {feature_id} has no linked evidence")
    elif not all(evidence.get("status") == "passed" for evidence in linked_evidence):
        failures.append(f"Required feature {feature_id} has non-passed linked evidence")
    return failures


def evaluate_required_feature_failures(
    feature_id: str,
    index: dict[str, dict[str, dict[str, Any]]],
) -> list[str]:
    memo: dict[str, list[str]] = {}

    def visit(current_feature_id: str, stack: list[str]) -> list[str]:
        if current_feature_id in memo:
            return memo[current_feature_id]
        feature = index["features"].get(current_feature_id)
        if feature is None:
            failures = [f"Missing feature {current_feature_id}"]
            memo[current_feature_id] = failures
            return failures
        if current_feature_id in stack:
            cycle = " -> ".join(stack + [current_feature_id])
            failures = [f"Feature requirement cycle detected: {cycle}"]
            memo[current_feature_id] = failures
            return failures

        failures = _feature_direct_proof_failures(feature, index)
        requires = feature.get("requires", [])
        if isinstance(requires, list):
            for required_feature_id in requires:
                if required_feature_id not in index["features"]:
                    failures.append(f"Required feature {required_feature_id} referenced by {current_feature_id} does not exist")
                    continue
                child_failures = visit(required_feature_id, stack + [current_feature_id])
                failures.extend(child_failures)
        memo[current_feature_id] = sorted(set(failures))
        return memo[current_feature_id]

    feature = index["features"].get(feature_id)
    if feature is None:
        return [f"Missing feature {feature_id}"]

    requires = feature.get("requires", [])
    if not requires:
        return []

    failures: list[str] = []
    for required_feature_id in requires:
        if required_feature_id not in index["features"]:
            failures.append(f"Feature {feature_id} requires missing feature {required_feature_id}")
            continue
        child_failures = visit(required_feature_id, [feature_id])
        if child_failures:
            failures.extend(f"Feature {feature_id} requires {required_feature_id} to be passing: {failure}" for failure in child_failures)
    return sorted(set(failures))
