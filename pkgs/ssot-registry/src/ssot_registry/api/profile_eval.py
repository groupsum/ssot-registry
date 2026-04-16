from __future__ import annotations

from typing import Any

from ssot_registry.guards.claim_closure import evaluate_claim_guard
from ssot_registry.guards.feature_requirements import evaluate_required_feature_failures
from ssot_registry.model.enums import CLAIM_TIER_RANK
from ssot_registry.validators.identity import build_index

from .load import load_registry


def _effective_feature_required_tier(
    feature: dict[str, Any],
    *,
    profile_claim_tier: str | None = None,
    minimum_tier: str | None = None,
) -> str | None:
    feature_tier = feature.get("plan", {}).get("target_claim_tier")
    return feature_tier or minimum_tier or profile_claim_tier


def evaluate_feature_passing(
    feature: dict[str, object],
    index: dict[str, dict[str, dict[str, object]]],
    guard_policies: dict[str, object],
    *,
    minimum_tier: str | None = None,
) -> dict[str, object]:
    feature_id = str(feature["id"])
    required_tier = _effective_feature_required_tier(feature, minimum_tier=minimum_tier)
    failures: list[str] = []
    checks: dict[str, bool] = {}

    checks["implemented"] = feature.get("implementation_status") == "implemented"
    if not checks["implemented"]:
        failures.append(f"Feature {feature_id} is not implemented")

    requirement_failures = evaluate_required_feature_failures(feature_id, index)
    checks["required_features_passing"] = not requirement_failures
    failures.extend(requirement_failures)

    checked_claim_ids: list[str] = []
    satisfying_claim_ids: list[str] = []
    for claim_id in feature.get("claim_ids", []):
        if claim_id not in index["claims"]:
            continue
        checked_claim_ids.append(claim_id)
        claim = index["claims"][claim_id]
        guard = evaluate_claim_guard(claim, index, guard_policies)
        if not guard.get("passed"):
            continue
        if required_tier is not None and CLAIM_TIER_RANK[claim["tier"]] < CLAIM_TIER_RANK[required_tier]:
            continue
        satisfying_claim_ids.append(claim_id)

    checks["claim_target_met"] = bool(satisfying_claim_ids) if required_tier is not None else bool(checked_claim_ids)
    if not checks["claim_target_met"]:
        if required_tier is None:
            failures.append(f"Feature {feature_id} has no effective required claim tier")
        else:
            failures.append(f"Feature {feature_id} has no satisfying claim at or above tier {required_tier}")

    return {
        "feature_id": feature_id,
        "passed": not failures,
        "required_tier": required_tier,
        "satisfying_claim_ids": sorted(satisfying_claim_ids),
        "checked_claim_ids": sorted(checked_claim_ids),
        "failures": sorted(set(failures)),
        "checks": checks,
    }


def resolve_profile_features(
    profile: dict[str, object],
    index: dict[str, dict[str, dict[str, object]]],
) -> tuple[list[str], list[str]]:
    resolved: list[str] = []
    failures: list[str] = []
    seen_features: set[str] = set()

    def add_feature(feature_id: str) -> None:
        if feature_id in seen_features:
            return
        seen_features.add(feature_id)
        resolved.append(feature_id)

    def visit_profile(profile_id: str, stack: list[str]) -> None:
        if profile_id in stack:
            failures.append(f"Profile requirement cycle detected: {' -> '.join(stack + [profile_id])}")
            return
        current = index["profiles"].get(profile_id)
        if current is None:
            failures.append(f"Missing profile {profile_id}")
            return
        for feature_id in current.get("feature_ids", []):
            if feature_id not in index["features"]:
                failures.append(f"Profile {profile_id} references missing feature {feature_id}")
                continue
            add_feature(feature_id)
        for nested_profile_id in current.get("profile_ids", []):
            if nested_profile_id not in index["profiles"]:
                failures.append(f"Profile {profile_id} requires missing profile {nested_profile_id}")
                continue
            visit_profile(nested_profile_id, stack + [profile_id])

    for feature_id in profile.get("feature_ids", []):
        if feature_id not in index["features"]:
            failures.append(f"Profile {profile['id']} references missing feature {feature_id}")
            continue
        add_feature(feature_id)
    for nested_profile_id in profile.get("profile_ids", []):
        visit_profile(nested_profile_id, [str(profile["id"])])

    return resolved, sorted(set(failures))


def evaluate_profile(
    profile: dict[str, object],
    index: dict[str, dict[str, dict[str, object]]],
    guard_policies: dict[str, object],
) -> dict[str, object]:
    resolved_feature_ids, resolution_failures = resolve_profile_features(profile, index)
    feature_results: list[dict[str, object]] = []
    for feature_id in resolved_feature_ids:
        feature = index["features"][feature_id]
        feature_results.append(
            evaluate_feature_passing(
                feature,
                index,
                guard_policies,
                minimum_tier=profile.get("claim_tier"),
            )
        )
    failures = list(resolution_failures)
    failures.extend(failure for row in feature_results for failure in row.get("failures", []))
    checks = {
        "has_features": bool(resolved_feature_ids),
        "all_features_passing": all(row.get("passed", False) for row in feature_results) if feature_results else False,
    }
    if not checks["has_features"]:
        failures.append(f"Profile {profile['id']} resolved to zero features")
    return {
        "profile_id": profile["id"],
        "passed": not failures,
        "resolved_feature_ids": resolved_feature_ids,
        "feature_results": feature_results,
        "failures": sorted(set(failures)),
        "checks": checks,
    }


def evaluate_profiles(
    index: dict[str, dict[str, dict[str, object]]],
    guard_policies: dict[str, object],
) -> dict[str, dict[str, object]]:
    return {
        profile_id: evaluate_profile(profile, index, guard_policies)
        for profile_id, profile in sorted(index["profiles"].items())
    }


def evaluate_profile_by_id(path: str, profile_id: str) -> dict[str, object]:
    registry_path, _repo_root, registry = load_registry(path)
    index = build_index(registry, [])
    profile = index["profiles"].get(profile_id)
    if profile is None:
        raise ValueError(f"Unknown profile id: {profile_id}")
    result = evaluate_profile(profile, index, registry.get("guard_policies", {}))
    return {
        "passed": bool(result["passed"]),
        "registry_path": registry_path.as_posix(),
        "profile": result,
    }
