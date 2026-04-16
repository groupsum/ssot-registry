from __future__ import annotations

from ssot_registry.api.profile_eval import evaluate_profile
from ssot_registry.model.registry import count_entities
from ssot_registry.validators.identity import build_index


def build_summary(registry: dict[str, object]) -> dict[str, object]:
    index = build_index(registry, [])
    passing = 0
    failing = 0
    draft = 0
    for profile in registry.get("profiles", []):
        if profile.get("status") == "draft":
            draft += 1
            continue
        result = evaluate_profile(profile, index, registry.get("guard_policies", {}))
        if result["passed"]:
            passing += 1
        else:
            failing += 1

    return {
        "counts": count_entities(registry),
        "profile_status": {
            "passing": passing,
            "failing": failing,
            "draft": draft,
        },
    }
