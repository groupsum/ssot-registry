from __future__ import annotations

from typing import Any

from ssot_registry.model.enums import ENTITY_PREFIXES, ENTITY_SECTIONS
from ssot_registry.model.ids import is_normalized_id


def build_index(registry: dict[str, Any], failures: list[str]) -> dict[str, dict[str, dict[str, Any]]]:
    index: dict[str, dict[str, dict[str, Any]]] = {}
    global_seen: dict[str, str] = {}

    for section in ENTITY_SECTIONS:
        rows = registry.get(section, [])
        if not isinstance(rows, list):
            failures.append(f"Top-level section {section} must be a list")
            rows = []

        local: dict[str, dict[str, Any]] = {}
        expected_prefix = ENTITY_PREFIXES[section]
        for row in rows:
            if not isinstance(row, dict):
                failures.append(f"Section {section} contains a non-object row")
                continue
            entity_id = row.get("id")
            if not isinstance(entity_id, str):
                failures.append(f"Section {section} row has a non-string id")
                continue
            if not entity_id.startswith(expected_prefix):
                failures.append(f"{section}.{entity_id} must start with {expected_prefix}")
            if not is_normalized_id(entity_id):
                failures.append(f"{section}.{entity_id} is not a normalized id")
            if entity_id in local:
                failures.append(f"Duplicate id in {section}: {entity_id}")
            if entity_id in global_seen:
                failures.append(f"Duplicate id across sections: {entity_id} in {section} and {global_seen[entity_id]}")
            global_seen[entity_id] = section
            local[entity_id] = row
        index[section] = local

    return index


def validate_identity(registry: dict[str, Any], failures: list[str]) -> dict[str, dict[str, dict[str, Any]]]:
    repo = registry.get("repo")
    if not isinstance(repo, dict):
        failures.append("Top-level repo must be an object")
    else:
        repo_id = repo.get("id")
        if not isinstance(repo_id, str):
            failures.append("repo.id must be a string")
        elif not repo_id.startswith("repo:"):
            failures.append(f"repo.id must start with repo:, got {repo_id}")
        elif not is_normalized_id(repo_id):
            failures.append(f"repo.id is not a normalized id: {repo_id}")
    return build_index(registry, failures)
