from __future__ import annotations

from typing import Any

from ssot_registry.model.enums import ASSURANCE_ENTITY_SECTIONS, ASSURANCE_ORIGINS
from ssot_registry.model.registry import normalize_repo_kind


def _repo_kind(registry: dict[str, Any]) -> str:
    repo = registry.get("repo")
    if isinstance(repo, dict):
        return normalize_repo_kind(repo.get("kind"))
    return "repo-local"


def validate_assurance_origins(
    registry: dict[str, Any],
    index: dict[str, dict[str, dict[str, Any]]],
    failures: list[str],
) -> None:
    repo_kind = _repo_kind(registry)
    for section in ASSURANCE_ENTITY_SECTIONS:
        for entity_id, row in index.get(section, {}).items():
            origin = row.get("origin")
            if origin not in ASSURANCE_ORIGINS:
                continue
            if repo_kind == "repo-local" and origin == "ssot-core":
                failures.append(
                    f"{section}.{entity_id}.origin cannot be ssot-core in a repo-local registry; "
                    "sync ssot-origin obligations or author repo-local rows instead"
                )
