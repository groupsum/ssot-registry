from __future__ import annotations

from ssot_registry.model.enums import CLAIM_STATUS_RANK, CLAIM_TIER_RANK


def evaluate_claim_guard(
    claim: dict[str, object],
    index: dict[str, dict[str, dict[str, object]]],
    guard_policies: dict[str, object],
) -> dict[str, object]:
    failures: list[str] = []
    checks: dict[str, bool] = {}

    linked_features = [index["features"][feature_id] for feature_id in claim.get("feature_ids", []) if feature_id in index["features"]]
    linked_tests = [index["tests"][test_id] for test_id in claim.get("test_ids", []) if test_id in index["tests"]]
    linked_evidence = [index["evidence"][evidence_id] for evidence_id in claim.get("evidence_ids", []) if evidence_id in index["evidence"]]

    require_implemented_features = bool(guard_policies.get("claim_closure", {}).get("require_implemented_features", True))
    if require_implemented_features:
        checks["implemented_features"] = bool(linked_features) and all(
            feature.get("implementation_status") == "implemented" for feature in linked_features
        )
        if not checks["implemented_features"]:
            failures.append(
                f"Claim {claim['id']} requires implemented linked features"
            )

    require_linked_tests_passing = bool(guard_policies.get("claim_closure", {}).get("require_linked_tests_passing", True))
    if require_linked_tests_passing:
        checks["tests_passing"] = bool(linked_tests) and all(test.get("status") == "passing" for test in linked_tests)
        if not checks["tests_passing"]:
            failures.append(f"Claim {claim['id']} requires all linked tests to be passing")

    require_linked_evidence_passing = bool(guard_policies.get("claim_closure", {}).get("require_linked_evidence_passing", True))
    if require_linked_evidence_passing:
        checks["evidence_passing"] = bool(linked_evidence) and all(evidence.get("status") == "passed" for evidence in linked_evidence)
        if not checks["evidence_passing"]:
            failures.append(f"Claim {claim['id']} requires all linked evidence rows to be passed")

    forbid_failed_or_stale_evidence = bool(guard_policies.get("claim_closure", {}).get("forbid_failed_or_stale_evidence", True))
    if forbid_failed_or_stale_evidence:
        checks["no_failed_or_stale_evidence"] = all(
            evidence.get("status") not in {"failed", "stale"} for evidence in linked_evidence
        )
        if not checks["no_failed_or_stale_evidence"]:
            failures.append(f"Claim {claim['id']} has linked evidence rows in failed or stale status")

    require_claim_evidence_tier_alignment = bool(
        guard_policies.get("claim_closure", {}).get("require_claim_evidence_tier_alignment", True)
    )
    if require_claim_evidence_tier_alignment:
        checks["evidence_tier_alignment"] = bool(linked_evidence) and any(
            CLAIM_TIER_RANK[evidence["tier"]] >= CLAIM_TIER_RANK[claim["tier"]] and evidence.get("status") == "passed"
            for evidence in linked_evidence
        )
        if not checks["evidence_tier_alignment"]:
            failures.append(
                f"Claim {claim['id']} requires passed linked evidence at or above claim tier {claim['tier']}"
            )

    feature_target_failures: list[str] = []
    for feature in linked_features:
        feature_target_tier = feature.get("plan", {}).get("target_claim_tier")
        if feature_target_tier is not None and CLAIM_TIER_RANK[claim["tier"]] < CLAIM_TIER_RANK[feature_target_tier]:
            feature_target_failures.append(
                f"Claim {claim['id']} tier {claim['tier']} is below feature target tier {feature_target_tier} on {feature['id']}"
            )
    checks["feature_target_alignment"] = not feature_target_failures
    failures.extend(feature_target_failures)

    current_status_rank = CLAIM_STATUS_RANK.get(claim.get("status"), -999)
    recommended_status = claim.get("status")
    if not failures:
        if current_status_rank < CLAIM_STATUS_RANK["certified"]:
            recommended_status = "certified"
        else:
            recommended_status = claim.get("status")

    return {
        "claim_id": claim["id"],
        "passed": not failures,
        "failures": failures,
        "checks": checks,
        "recommended_status": recommended_status,
    }
