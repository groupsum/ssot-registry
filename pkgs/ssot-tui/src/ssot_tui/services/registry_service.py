from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ssot_contracts.generated.python.tui_metadata import ENTITY_SECTIONS
from ssot_registry.api import create_entity, delete_entity, list_entities, load_registry, update_entity, validate_registry
from ssot_registry.api.documents import list_documents


@dataclass(slots=True)
class RegistryWorkspace:
    root_path: str
    registry_path: str
    repo: dict[str, Any]
    validation: dict[str, Any]
    collections: dict[str, list[dict[str, Any]]]


class RegistryWorkspaceService:
    def load_workspace(self, path: str | Path) -> RegistryWorkspace:
        registry_path, repo_root, registry = load_registry(path)
        collections: dict[str, list[dict[str, Any]]] = {}
        for section, _label in ENTITY_SECTIONS:
            if section == "adrs":
                payload = list_documents(repo_root, "adr")
                collections[section] = payload.get("documents", [])
                continue
            if section == "specs":
                payload = list_documents(repo_root, "spec")
                collections[section] = payload.get("documents", [])
                continue
            payload = list_entities(repo_root, section)
            collections[section] = payload.get("entities", [])

        return RegistryWorkspace(
            root_path=repo_root.as_posix(),
            registry_path=registry_path.as_posix(),
            repo=registry.get("repo", {}),
            validation=validate_registry(repo_root),
            collections=collections,
        )

    def create(self, path: str | Path, section: str, payload: dict[str, Any]) -> dict[str, Any]:
        return create_entity(path, section, payload)

    def update(self, path: str | Path, section: str, entity_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return update_entity(path, section, entity_id, payload)

    def delete(self, path: str | Path, section: str, entity_id: str) -> dict[str, Any]:
        return delete_entity(path, section, entity_id)

    def section_counts(self, workspace: RegistryWorkspace) -> dict[str, int]:
        return {section: len(rows) for section, rows in workspace.collections.items()}
