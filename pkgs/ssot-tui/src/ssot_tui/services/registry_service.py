from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ssot_contracts.generated.python.tui_metadata import ENTITY_SECTIONS
from ssot_registry.api import create_entity, delete_entity, list_entities, load_registry, update_entity, validate_registry
from ssot_registry.api.documents import list_documents, load_document_payload_for_row


@dataclass(slots=True)
class RegistryWorkspace:
    root_path: str
    registry_path: str
    registry_version: str
    registry_schema_version: str
    repo: dict[str, Any]
    validation: dict[str, Any]
    collections: dict[str, list[dict[str, Any]]]


class RegistryWorkspaceService:
    def load_workspace(self, path: str | Path) -> RegistryWorkspace:
        registry_path, repo_root, registry = load_registry(path)
        collections: dict[str, list[dict[str, Any]]] = {}
        for section, _label in ENTITY_SECTIONS:
            if section == "adrs":
                collections[section] = list_documents(repo_root, "adr")
                continue
            if section == "specs":
                collections[section] = list_documents(repo_root, "spec")
                continue
            collections[section] = [self._project_display_fields(row) for row in list_entities(repo_root, section)]

        return RegistryWorkspace(
            root_path=repo_root.as_posix(),
            registry_path=registry_path.as_posix(),
            registry_version=str(registry.get("tooling", {}).get("ssot_registry_version", "unknown")),
            registry_schema_version=str(registry.get("schema_version", "unknown")),
            repo=registry.get("repo", {}),
            validation=validate_registry(repo_root),
            collections=collections,
        )

    def _project_display_fields(self, row: dict[str, Any]) -> dict[str, Any]:
        projected = dict(row)
        plan = projected.get("plan")
        if isinstance(plan, dict):
            # Expose nested planning attributes as flat fields so table columns
            # can display planning state (for example out_of_bounds horizon).
            projected.setdefault("horizon", plan.get("horizon"))
            projected.setdefault("slot", plan.get("slot"))
            projected.setdefault("target_claim_tier", plan.get("target_claim_tier"))
            projected.setdefault("target_lifecycle_stage", plan.get("target_lifecycle_stage"))
        return projected

    def create(self, path: str | Path, section: str, payload: dict[str, Any]) -> dict[str, Any]:
        return create_entity(path, section, payload)

    def update(self, path: str | Path, section: str, entity_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return update_entity(path, section, entity_id, payload)

    def delete(self, path: str | Path, section: str, entity_id: str) -> dict[str, Any]:
        return delete_entity(path, section, entity_id)

    def section_counts(self, workspace: RegistryWorkspace) -> dict[str, int]:
        return {section: len(rows) for section, rows in workspace.collections.items()}

    def build_detail_entity(self, repo_root: str | Path, section: str, entity: dict[str, Any]) -> dict[str, Any]:
        if section not in {"adrs", "specs"}:
            return entity

        kind = "adr" if section == "adrs" else "spec"
        detail = dict(entity)
        payload = load_document_payload_for_row(Path(repo_root), entity, kind)
        detail["summary"] = payload["summary"]
        detail["body"] = payload["body"]
        detail["decision_date"] = payload.get("decision_date")
        detail["tags"] = list(payload.get("tags", []))
        detail["references"] = list(payload.get("references", []))
        if kind == "spec":
            detail["spec_kind"] = payload.get("spec_kind", entity.get("kind"))
        return detail
