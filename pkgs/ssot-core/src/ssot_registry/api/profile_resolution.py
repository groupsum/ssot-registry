from __future__ import annotations


def resolve_boundary_feature_ids(
    boundary: dict[str, object],
    index: dict[str, dict[str, dict[str, object]]],
) -> list[str]:
    resolved: list[str] = []
    seen: set[str] = set()

    def add_feature(feature_id: str) -> None:
        if feature_id in seen:
            return
        if feature_id in index["features"]:
            seen.add(feature_id)
            resolved.append(feature_id)

    def visit_profile(profile_id: str, stack: list[str]) -> None:
        if profile_id in stack:
            return
        profile = index["profiles"].get(profile_id)
        if profile is None:
            return
        for feature_id in profile.get("feature_ids", []):
            add_feature(feature_id)
        for nested_profile_id in profile.get("profile_ids", []):
            visit_profile(nested_profile_id, stack + [profile_id])

    for feature_id in boundary.get("feature_ids", []):
        add_feature(feature_id)
    for profile_id in boundary.get("profile_ids", []):
        visit_profile(profile_id, [])
    return resolved
