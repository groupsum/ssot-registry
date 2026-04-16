from __future__ import annotations

from typing import Any


def resolve_profile_ids_transitively(
    profile_id: str,
    index: dict[str, dict[str, dict[str, Any]]],
) -> tuple[list[str], list[str]]:
    ordered: list[str] = []
    failures: list[str] = []
    visiting: list[str] = []
    visited: set[str] = set()

    def visit(current_profile_id: str) -> None:
        profile = index["profiles"].get(current_profile_id)
        if profile is None:
            failures.append(f"Missing profile {current_profile_id}")
            return
        if current_profile_id in visiting:
            cycle = " -> ".join(visiting + [current_profile_id])
            failures.append(f"Profile requirement cycle detected: {cycle}")
            return
        if current_profile_id in visited:
            return
        visiting.append(current_profile_id)
        for nested_profile_id in profile.get("profile_ids", []):
            visit(nested_profile_id)
            if nested_profile_id in index["profiles"] and nested_profile_id not in ordered:
                ordered.append(nested_profile_id)
        visiting.pop()
        visited.add(current_profile_id)

    visit(profile_id)
    return ordered, sorted(set(failures))


def evaluate_required_profile_failures(
    profile_id: str,
    index: dict[str, dict[str, dict[str, Any]]],
) -> list[str]:
    profile = index["profiles"].get(profile_id)
    if profile is None:
        return [f"Missing profile {profile_id}"]

    failures: list[str] = []
    _, transitive_failures = resolve_profile_ids_transitively(profile_id, index)
    failures.extend(transitive_failures)

    for nested_profile_id in profile.get("profile_ids", []):
        if nested_profile_id not in index["profiles"]:
            failures.append(f"Profile {profile_id} requires missing profile {nested_profile_id}")

    return sorted(set(failures))
