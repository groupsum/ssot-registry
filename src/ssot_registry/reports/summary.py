from __future__ import annotations

from ssot_registry.api.profile_eval import evaluate_profiles
from ssot_registry.model.registry import count_entities
from ssot_registry.validators.identity import build_index


def build_summary(registry: dict[str, object]) -> dict[str, object]:
    index = build_index(registry, [])
    profile_status = {"passing": 0, "failing": 0, "draft": 0}
    profile_results = evaluate_profiles(index, registry.get("guard_policies", {}))
    for profile_id, profile in index["profiles"].items():
        if profile.get("status") == "draft":
            profile_status["draft"] += 1
        elif profile_results.get(profile_id, {}).get("passed"):
            profile_status["passing"] += 1
        else:
            profile_status["failing"] += 1
    return {
        "counts": count_entities(registry),
        "profile_status": profile_status,
    }
