from __future__ import annotations

from typing import Any

from ssot_registry.model.enums import CLAIM_TIER_RANK


def _effective_feature_required_tier(
    feature: dict[str, Any],
    *,
    profile_claim_tier: str | None,
) -> str | None:
    plan = feature.get("plan", {})
    if isinstance(plan, dict) and plan.get("target_claim_tier") is not None:
        return plan.get("target_claim_tier")
    if profile_claim_tier is not None:
        return profile_claim_tier
    return None


def evaluate_feature_passing(
    feature: dict[str, object],
    index: dict[str, dict[str, dict[str, object]]],
    guard_policies: dict[str, object],
    *,
    minimum_tier: str | None = None,
) -> dict[str, object]:
    from ssot_registry.guards.claim_closure import evaluate_claim_guard
    from ssot_registry.guards.feature_requirements import evaluate_required_feature_failures

    feature_id = str(feature["id"])
    failures: list[str] = []
    checked_claim_ids: list[str] = []
    satisfying_claim_ids: list[str] = []

    implemented = feature.get("implementation_status") == "implemented"
    if not implemented:
        failures.append(f"Feature {feature_id} is not implemented")

    required_feature_failures = evaluate_required_feature_failures(feature_id, index)
    if required_feature_failures:
        failures.extend(required_feature_failures)

    for claim_id in feature.get("claim_ids", []):
        if claim_id not in index["claims"]:
            failures.append(f"Feature {feature_id} references missing claim {claim_id}")
            continue
        checked_claim_ids.append(claim_id)
        claim = index["claims"][claim_id]
        guard = evaluate_claim_guard(claim, index, guard_policies)
        if not guard["passed"]:
            continue
        if minimum_tier is not None and CLAIM_TIER_RANK[claim["tier"]] < CLAIM_TIER_RANK[minimum_tier]:
            continue
        satisfying_claim_ids.append(claim_id)

    required_tier = minimum_tier
    claim_target_met = bool(satisfying_claim_ids)
    if required_tier is None:
        claim_target_met = bool(satisfying_claim_ids)
    if not checked_claim_ids:
        failures.append(f"Feature {feature_id} has no linked claims")
    if not claim_target_met:
        failures.append(f"Feature {feature_id} has no satisfying claim at required tier")

    return {
        "feature_id": feature_id,
        "passed": implemented and not required_feature_failures and claim_target_met,
        "required_tier": required_tier,
        "satisfying_claim_ids": sorted(set(satisfying_claim_ids)),
        "checked_claim_ids": sorted(set(checked_claim_ids)),
        "failures": sorted(set(failures)),
        "checks": {
            "implemented": implemented,
            "required_features_passing": not required_feature_failures,
            "claim_target_met": claim_target_met,
        },
    }


def resolve_profile_features(
    profile: dict[str, object],
    index: dict[str, dict[str, dict[str, object]]],
) -> tuple[list[str], list[str]]:
    from ssot_registry.guards.profile_requirements import evaluate_required_profile_failures

    resolved: list[str] = []
    failures = evaluate_required_profile_failures(str(profile["id"]), index)
    visited_profiles: set[str] = set()

    def add_feature(feature_id: str) -> None:
        if feature_id not in resolved:
            resolved.append(feature_id)

    def visit_profile(profile_id: str, stack: list[str]) -> None:
        row = index["profiles"].get(profile_id)
        if row is None:
            failures.append(f"Missing profile {profile_id}")
            return
        if profile_id in stack:
            cycle = " -> ".join(stack + [profile_id])
            failures.append(f"Profile requirement cycle detected: {cycle}")
            return
        for feature_id in row.get("feature_ids", []):
            if feature_id not in index["features"]:
                failures.append(f"Profile {profile_id} references missing feature {feature_id}")
            else:
                add_feature(feature_id)
        if profile_id in visited_profiles:
            return
        visited_profiles.add(profile_id)
        for nested_profile_id in row.get("profile_ids", []):
            visit_profile(nested_profile_id, stack + [profile_id])

    visit_profile(str(profile["id"]), [])
    return resolved, sorted(set(failures))


def evaluate_profile(
    profile: dict[str, object],
    index: dict[str, dict[str, dict[str, object]]],
    guard_policies: dict[str, object],
) -> dict[str, object]:
    profile_id = str(profile["id"])
    resolved_feature_ids, failures = resolve_profile_features(profile, index)

    feature_results: list[dict[str, object]] = []
    for feature_id in resolved_feature_ids:
        feature = index["features"][feature_id]
        required_tier = _effective_feature_required_tier(feature, profile_claim_tier=profile.get("claim_tier"))
        feature_results.append(
            evaluate_feature_passing(feature, index, guard_policies, minimum_tier=required_tier)
        )

    passed = not failures and all(result["passed"] for result in feature_results)
    checks = {
        "features_resolved": not failures,
        "all_features_passing": all(result["passed"] for result in feature_results),
    }
    return {
        "profile_id": profile_id,
        "passed": passed,
        "resolved_feature_ids": resolved_feature_ids,
        "feature_results": feature_results,
        "failures": sorted(set(failures)),
        "checks": checks,
    }


def evaluate_profiles(
    index: dict[str, dict[str, dict[str, object]]],
    guard_policies: dict[str, object],
) -> list[dict[str, object]]:
    return [
        evaluate_profile(index["profiles"][profile_id], index, guard_policies)
        for profile_id in sorted(index.get("profiles", {}))
    ]
