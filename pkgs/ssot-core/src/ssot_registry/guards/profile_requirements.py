from __future__ import annotations

from typing import Any


def resolve_profile_ids_transitively(
    profile_id: str,
    index: dict[str, dict[str, dict[str, Any]]],
) -> tuple[list[str], list[str]]:
    resolved: list[str] = []
    failures: list[str] = []
    seen: set[str] = set()

    def visit(current_profile_id: str, stack: list[str]) -> None:
        if current_profile_id in stack:
            cycle = " -> ".join(stack + [current_profile_id])
            failures.append(f"Profile requirement cycle detected: {cycle}")
            return
        profile = index["profiles"].get(current_profile_id)
        if profile is None:
            failures.append(f"Missing profile {current_profile_id}")
            return
        for nested_profile_id in profile.get("profile_ids", []):
            if nested_profile_id not in index["profiles"]:
                failures.append(f"Profile {current_profile_id} requires missing profile {nested_profile_id}")
                continue
            if nested_profile_id not in seen:
                seen.add(nested_profile_id)
                resolved.append(nested_profile_id)
            visit(nested_profile_id, stack + [current_profile_id])

    visit(profile_id, [])
    return resolved, sorted(set(failures))


def evaluate_required_profile_failures(
    profile_id: str,
    index: dict[str, dict[str, dict[str, object]]],
) -> list[str]:
    if profile_id not in index["profiles"]:
        return [f"Missing profile {profile_id}"]
    _resolved, failures = resolve_profile_ids_transitively(profile_id, index)
    return failures
