from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from ssot_registry.guards.claim_tier_gates import evaluate_claim_tier_gate
from ssot_registry.model.enums import CLAIM_TIER_RANK
from ssot_registry.util.jsonio import stable_json_dumps

from ssot_registry.control.paths import ensure_allowed_path, path_overlaps

MATURATION_TIERS = ("T0", "T1", "T2", "T3", "T4")


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
) -> dict[str, Any] | None:
    root = Path(repo_root) if repo_root is not None else None
    active_roots = active_path_roots or []
    candidates: list[dict[str, Any]] = []
    for feature in registry.get("features", []):
        if not isinstance(feature, dict) or not _is_in_bounds(feature):
            continue
        feature_target = _feature_target_tier(feature, target_tier)
        if CLAIM_TIER_RANK[feature_target] > CLAIM_TIER_RANK[target_tier]:
            feature_target = target_tier
        current = current_verified_tier(registry, feature, repo_root=root)
        to_tier = next_tier(current, feature_target)
        if to_tier is None:
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


def campaign_completion(
    registry: dict[str, Any],
    *,
    target_tier: str = "T2",
    repo_root: str | Path | None = None,
    active_lease_count: int = 0,
) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else None
    incomplete: list[dict[str, str]] = []
    out_of_bounds: list[str] = []
    for feature in registry.get("features", []):
        if not isinstance(feature, dict):
            continue
        if not _is_in_bounds(feature):
            out_of_bounds.append(str(feature.get("id")))
            continue
        feature_target = _feature_target_tier(feature, target_tier)
        if CLAIM_TIER_RANK[feature_target] > CLAIM_TIER_RANK[target_tier]:
            feature_target = target_tier
        current = current_verified_tier(registry, feature, repo_root=root)
        if CLAIM_TIER_RANK[current] < CLAIM_TIER_RANK[feature_target]:
            incomplete.append({"feature_id": str(feature.get("id")), "current_tier": current, "target_tier": feature_target})
    return {
        "complete": not incomplete and active_lease_count == 0,
        "target_tier": target_tier,
        "incomplete": incomplete,
        "out_of_bounds": sorted(out_of_bounds),
        "active_lease_count": active_lease_count,
    }
