from __future__ import annotations

from typing import Any


def validate_feature_parent_links(
    index: dict[str, dict[str, dict[str, Any]]],
    failures: list[str],
) -> None:
    features = index.get("features", {})

    for feature_id, feature in features.items():
        parent_ids = feature.get("parent_feature_ids", [])
        if not isinstance(parent_ids, list):
            continue
        if feature_id in parent_ids:
            failures.append(f"features.{feature_id}.parent_feature_ids must not include itself")
        duplicates = sorted({parent_id for parent_id in parent_ids if parent_ids.count(parent_id) > 1})
        if duplicates:
            failures.append(
                f"features.{feature_id}.parent_feature_ids contains duplicate ids: {', '.join(duplicates)}"
            )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(feature_id: str, stack: list[str]) -> None:
        if feature_id in visiting:
            cycle_start = stack.index(feature_id) if feature_id in stack else 0
            cycle = " -> ".join(stack[cycle_start:] + [feature_id])
            failures.append(f"Feature parent cycle detected: {cycle}")
            return
        if feature_id in visited:
            return
        feature = features.get(feature_id)
        if feature is None:
            return

        visiting.add(feature_id)
        parent_ids = feature.get("parent_feature_ids", [])
        if isinstance(parent_ids, list):
            for parent_id in parent_ids:
                if parent_id in features:
                    visit(parent_id, stack + [feature_id])
        visiting.remove(feature_id)
        visited.add(feature_id)

    for feature_id in features:
        visit(feature_id, [])
