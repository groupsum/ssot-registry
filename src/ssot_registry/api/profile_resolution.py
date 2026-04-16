from __future__ import annotations

from typing import Any

from .profile_eval import resolve_profile_features


def resolve_boundary_feature_ids(
    boundary: dict[str, object],
    index: dict[str, dict[str, dict[str, Any]]],
) -> list[str]:
    resolved: list[str] = []

    def add_feature(feature_id: str) -> None:
        if feature_id in index["features"] and feature_id not in resolved:
            resolved.append(feature_id)

    for feature_id in boundary.get("feature_ids", []):
        add_feature(feature_id)

    for profile_id in boundary.get("profile_ids", []):
        profile = index["profiles"].get(profile_id)
        if profile is None:
            continue
        feature_ids, _failures = resolve_profile_features(profile, index)
        for feature_id in feature_ids:
            add_feature(feature_id)

    return resolved
