from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from ssot_registry.guards.claim_tier_gates import evaluate_claim_tier_gate
from ssot_registry.model.enums import CLAIM_TIER_RANK
from ssot_registry.util.jsonio import stable_json_dumps

from ssot_registry.control.paths import ensure_allowed_path, path_is_under, path_overlaps

MATURATION_TIERS = ("T0", "T1", "T2", "T3", "T4")
DEFAULT_FEATURE_LIMIT = 25


def build_registry_index(registry: dict[str, Any]) -> dict[str, dict[str, dict[str, Any]]]:
    return {
        section: {
            str(row["id"]): row
            for row in registry.get(section, [])
            if isinstance(row, dict) and isinstance(row.get("id"), str)
        }
        for section in ("features", "profiles", "tests", "claims", "evidence", "issues", "risks", "boundaries", "releases")
    }


def registry_content_hash(registry: dict[str, Any]) -> str:
    return hashlib.sha256(stable_json_dumps(registry).encode("utf-8")).hexdigest()


def _safe_slug(value: str) -> str:
    cleaned = value.split(":", 1)[-1]
    cleaned = re.sub(r"[^a-zA-Z0-9._/-]+", "-", cleaned).strip("-").lower()
    return cleaned or "feature"


def _as_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def _feature_target_tier(feature: dict[str, Any], default: str) -> str:
    plan = feature.get("plan") if isinstance(feature.get("plan"), dict) else {}
    target = plan.get("target_claim_tier") if isinstance(plan, dict) else None
    if isinstance(target, str) and target in CLAIM_TIER_RANK:
        return target
    return default


def _is_in_bounds(feature: dict[str, Any]) -> bool:
    plan = feature.get("plan") if isinstance(feature.get("plan"), dict) else {}
    lifecycle = feature.get("lifecycle") if isinstance(feature.get("lifecycle"), dict) else {}
    return plan.get("horizon") != "out_of_bounds" and lifecycle.get("stage", "active") == "active"


def normalize_feature_limit(limit: int | None = DEFAULT_FEATURE_LIMIT) -> int:
    if limit is None:
        return DEFAULT_FEATURE_LIMIT
    normalized = int(limit)
    if normalized < 1:
        raise ValueError("feature_limit must be at least 1")
    return normalized


def _iter_limited_in_bounds_features(
    registry: dict[str, Any],
    *,
    scope_feature_ids: set[str] | None = None,
    feature_limit: int | None = DEFAULT_FEATURE_LIMIT,
) -> list[dict[str, Any]]:
    limit = normalize_feature_limit(feature_limit)
    selected: list[dict[str, Any]] = []
    for feature in registry.get("features", []):
        if not isinstance(feature, dict):
            continue
        if scope_feature_ids is not None and str(feature.get("id")) not in scope_feature_ids:
            continue
        if not _is_in_bounds(feature):
            continue
        selected.append(feature)
        if len(selected) >= limit:
            break
    return selected


def current_verified_tier(
    registry: dict[str, Any],
    feature: dict[str, Any],
    *,
    repo_root: str | Path | None = None,
) -> str:
    index = build_registry_index(registry)
    approved = "T0"
    for claim_id in _as_string_list(feature.get("claim_ids")):
        claim = index["claims"].get(claim_id)
        if claim is None:
            continue
        claim_tier = str(claim.get("tier", "T0"))
        if claim_tier == "T0" and claim.get("status") in {"proposed", "declared", "implemented", "asserted", "evidenced"}:
            approved = max((approved, "T0"), key=lambda tier: CLAIM_TIER_RANK[tier])
            continue
        gate = evaluate_claim_tier_gate(registry, claim, index, repo_root=repo_root)
        if gate.get("passed"):
            approved = max((approved, str(gate.get("approved_tier", "T0"))), key=lambda tier: CLAIM_TIER_RANK[tier])
    return approved


def next_tier(current_tier: str, target_tier: str) -> str | None:
    if current_tier not in CLAIM_TIER_RANK or target_tier not in CLAIM_TIER_RANK:
        return None
    if CLAIM_TIER_RANK[current_tier] >= CLAIM_TIER_RANK[target_tier]:
        return None
    current_index = MATURATION_TIERS.index(current_tier)
    return MATURATION_TIERS[current_index + 1]


def derive_path_roots(feature: dict[str, Any]) -> list[str]:
    for key in ("lease_roots", "path_roots", "allowed_path_globs"):
        values = _as_string_list(feature.get(key))
        if values:
            return [ensure_allowed_path(value) for value in values]
    plan = feature.get("plan") if isinstance(feature.get("plan"), dict) else {}
    values = _as_string_list(plan.get("lease_roots") if isinstance(plan, dict) else None)
    if values:
        return [ensure_allowed_path(value) for value in values]
    slug = _safe_slug(str(feature.get("id", "feature")))
    return [ensure_allowed_path(f".ssot/evidence/{slug}")]


def _dependencies_ready(registry: dict[str, Any], feature: dict[str, Any], target_tier: str, repo_root: Path | None) -> bool:
    index = build_registry_index(registry)
    for dependency_id in _as_string_list(feature.get("requires")):
        dependency = index["features"].get(dependency_id)
        if dependency is None:
            return False
        if CLAIM_TIER_RANK[current_verified_tier(registry, dependency, repo_root=repo_root)] < CLAIM_TIER_RANK[target_tier]:
            return False
    return True


def next_maturation_slice(
    registry: dict[str, Any],
    *,
    target_tier: str = "T2",
    repo_root: str | Path | None = None,
    active_path_roots: list[str] | None = None,
    blocked_transitions: list[dict[str, Any]] | None = None,
    scope_feature_ids: set[str] | None = None,
    feature_limit: int | None = DEFAULT_FEATURE_LIMIT,
) -> dict[str, Any] | None:
    root = Path(repo_root) if repo_root is not None else None
    active_roots = active_path_roots or []
    blocked = {
        (str(item.get("feature_id")), str(item.get("from_tier")), str(item.get("to_tier")))
        for item in blocked_transitions or []
        if item.get("status", "open") == "open"
    }
    candidates: list[dict[str, Any]] = []
    for feature in _iter_limited_in_bounds_features(registry, scope_feature_ids=scope_feature_ids, feature_limit=feature_limit):
        feature_target = _feature_target_tier(feature, target_tier)
        if CLAIM_TIER_RANK[feature_target] > CLAIM_TIER_RANK[target_tier]:
            feature_target = target_tier
        current = current_verified_tier(registry, feature, repo_root=root)
        to_tier = next_tier(current, feature_target)
        if to_tier is None:
            continue
        if (str(feature["id"]), current, to_tier) in blocked:
            continue
        if not _dependencies_ready(registry, feature, current, root):
            continue
        roots = derive_path_roots(feature)
        if any(path_overlaps(root_path, active) for root_path in roots for active in active_roots):
            continue
        candidates.append(
            {
                "feature_id": feature["id"],
                "from_tier": current,
                "to_tier": to_tier,
                "target_tier": feature_target,
                "path_roots": roots,
                "priority": (CLAIM_TIER_RANK[current], len(roots), str(feature["id"])),
            }
        )
    if not candidates:
        return None
    selected = sorted(candidates, key=lambda item: item["priority"])[0]
    selected.pop("priority", None)
    return selected


def slice_actionability(
    registry: dict[str, Any],
    selected: dict[str, Any],
    *,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Return whether a selected slice can be worked without registry CRUD.

    Workers cannot edit `.ssot/registry.json`, so a slice is only worker-actionable
    when the target claim/test/evidence rows and links already exist. Workers may
    still create or update leased evidence artifacts and leased tests/runtime files.
    """

    index = build_registry_index(registry)
    feature_id = str(selected.get("feature_id", ""))
    to_tier = str(selected.get("to_tier", ""))
    lease_roots = [ensure_allowed_path(path) for path in _as_string_list(selected.get("path_roots"))]
    feature = index["features"].get(feature_id)
    failures: list[str] = []
    warnings: list[str] = []
    checks: dict[str, bool] = {
        "feature_exists": feature is not None,
        "lease_roots_present": bool(lease_roots),
    }

    if feature is None:
        failures.append(f"feature {feature_id} does not exist")
        return {"passed": False, "reason": "missing_feature", "failures": failures, "warnings": warnings, "checks": checks}
    if not lease_roots:
        failures.append(f"feature {feature_id} has no writable lease roots")

    target_claims = [
        index["claims"][claim_id]
        for claim_id in _as_string_list(feature.get("claim_ids"))
        if claim_id in index["claims"] and index["claims"][claim_id].get("tier") == to_tier
    ]
    checks["target_claim_exists"] = bool(target_claims)
    if not target_claims:
        failures.append(f"no linked {to_tier} claim found for feature {feature_id}")

    linked_tests = [
        index["tests"].get(test_id)
        for claim in target_claims
        for test_id in _as_string_list(claim.get("test_ids"))
    ]
    linked_tests = [test for test in linked_tests if test is not None]
    checks["target_claim_has_tests"] = bool(linked_tests)
    if target_claims and not linked_tests:
        warnings.append(f"linked {to_tier} claim for feature {feature_id} has no linked tests")

    linked_evidence = [
        index["evidence"].get(evidence_id)
        for claim in target_claims
        for evidence_id in _as_string_list(claim.get("evidence_ids"))
    ]
    linked_evidence = [evidence for evidence in linked_evidence if evidence is not None]
    checks["target_claim_has_evidence"] = bool(linked_evidence)
    if target_claims and not linked_evidence:
        warnings.append(f"linked {to_tier} claim for feature {feature_id} has no linked evidence")

    evidence_paths = [str(evidence.get("path")) for evidence in linked_evidence if isinstance(evidence.get("path"), str)]
    checks["evidence_paths_under_lease"] = bool(evidence_paths) and all(
        any(path_is_under(path, root) for root in lease_roots) for path in evidence_paths
    )
    if linked_evidence and not checks["evidence_paths_under_lease"]:
        warnings.append(f"linked {to_tier} evidence paths for feature {feature_id} are not under lease roots")

    root = Path(repo_root) if repo_root is not None else None
    missing_evidence_paths = [path for path in evidence_paths if root is not None and not (root / path).exists()]
    checks["missing_evidence_paths_are_writable"] = all(
        any(path_is_under(path, lease_root) for lease_root in lease_roots) for path in missing_evidence_paths
    )
    if missing_evidence_paths and not checks["missing_evidence_paths_are_writable"]:
        warnings.append(f"missing evidence artifacts for feature {feature_id} are outside lease roots")

    nonpassing_tests = [test for test in linked_tests if test.get("status") != "passing"]
    nonpassing_test_paths = [str(test.get("path")) for test in nonpassing_tests if isinstance(test.get("path"), str)]
    checks["nonpassing_tests_are_writable"] = all(
        any(path_is_under(path, lease_root) for lease_root in lease_roots) for path in nonpassing_test_paths
    )
    if nonpassing_tests and not checks["nonpassing_tests_are_writable"]:
        warnings.append(f"non-passing linked tests for feature {feature_id} are outside lease roots")

    if not failures and all(root.startswith(".ssot/evidence/") for root in lease_roots):
        warnings.append("slice has evidence-only lease roots; it is actionable only if linked tests are already passing")

    reason = "worker_actionable" if not failures else "missing_target_tier_claim_wiring"
    return {
        "passed": not failures,
        "reason": reason,
        "feature_id": feature_id,
        "from_tier": selected.get("from_tier"),
        "to_tier": to_tier,
        "lease_roots": lease_roots,
        "failures": sorted(set(failures)),
        "warnings": warnings,
        "checks": checks,
    }


def campaign_completion(
    registry: dict[str, Any],
    *,
    target_tier: str = "T2",
    repo_root: str | Path | None = None,
    active_lease_count: int = 0,
    scope_feature_ids: set[str] | None = None,
    feature_limit: int | None = DEFAULT_FEATURE_LIMIT,
) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else None
    incomplete: list[dict[str, str]] = []
    limited_features = _iter_limited_in_bounds_features(registry, scope_feature_ids=scope_feature_ids, feature_limit=feature_limit)
    for feature in limited_features:
        feature_target = _feature_target_tier(feature, target_tier)
        if CLAIM_TIER_RANK[feature_target] > CLAIM_TIER_RANK[target_tier]:
            feature_target = target_tier
        current = current_verified_tier(registry, feature, repo_root=root)
        if CLAIM_TIER_RANK[current] < CLAIM_TIER_RANK[feature_target]:
            incomplete.append({"feature_id": str(feature.get("id")), "current_tier": current, "target_tier": feature_target})
    return {
        "complete": not incomplete and active_lease_count == 0,
        "target_tier": target_tier,
        "feature_limit": normalize_feature_limit(feature_limit),
        "features_considered_count": len(limited_features),
        "incomplete": incomplete,
        "active_lease_count": active_lease_count,
    }
