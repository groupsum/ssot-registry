from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from ssot_registry.model.enums import ASSURANCE_ENTITY_SECTIONS
from ssot_registry.util.errors import ValidationError

from .load import load_registry
from .save import save_registry
from .validate import validate_registry_document


def _origin_rows(registry: dict[str, Any], section: str) -> dict[str, dict[str, Any]]:
    return {
        row["id"]: row
        for row in registry.get(section, [])
        if isinstance(row, dict) and isinstance(row.get("id"), str) and row.get("origin") == "ssot-origin"
    }


def _load_source_registry(source: str | Path | dict[str, Any]) -> dict[str, Any]:
    if isinstance(source, dict):
        return deepcopy(source)
    _registry_path, _repo_root, registry = load_registry(source)
    return registry


def sync_origin_assurance_rows(
    path: str | Path,
    source: str | Path | dict[str, Any],
    *,
    sections: list[str] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    registry_path, repo_root, registry = load_registry(path)
    source_registry = _load_source_registry(source)
    selected_sections = tuple(sections or ASSURANCE_ENTITY_SECTIONS)
    unsupported = sorted(set(selected_sections) - set(ASSURANCE_ENTITY_SECTIONS))
    if unsupported:
        raise ValueError(f"Unsupported assurance sections: {', '.join(unsupported)}")

    created: dict[str, list[str]] = {}
    updated: dict[str, list[str]] = {}
    unchanged: dict[str, list[str]] = {}
    blocked: dict[str, list[str]] = {}

    for section in selected_sections:
        created[section] = []
        updated[section] = []
        unchanged[section] = []
        blocked[section] = []
        source_rows = _origin_rows(source_registry, section)
        target_rows = registry.setdefault(section, [])
        target_by_id = {
            row["id"]: row for row in target_rows if isinstance(row, dict) and isinstance(row.get("id"), str)
        }
        for entity_id, source_row in sorted(source_rows.items()):
            target_row = target_by_id.get(entity_id)
            if target_row is None:
                created[section].append(entity_id)
                if not dry_run:
                    target_rows.append(deepcopy(source_row))
                continue
            if target_row.get("origin") != "ssot-origin":
                blocked[section].append(entity_id)
                continue
            if target_row == source_row:
                unchanged[section].append(entity_id)
                continue
            updated[section].append(entity_id)
            if not dry_run:
                target_row.clear()
                target_row.update(deepcopy(source_row))
        if not dry_run:
            registry[section] = sorted(target_rows, key=lambda row: row.get("id", ""))

    failures = [f"{section}.{entity_id} conflicts with a non-ssot-origin row" for section, ids in blocked.items() for entity_id in ids]
    if failures:
        raise ValidationError("; ".join(failures))

    validation = None
    if not dry_run:
        validation = validate_registry_document(registry, registry_path, repo_root)
        if not validation["passed"]:
            raise ValidationError("Registry validation failed after origin sync: " + "; ".join(validation["failures"]))
        save_registry(registry_path, registry)

    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "dry_run": dry_run,
        "created": created,
        "updated": updated,
        "unchanged": unchanged,
        "validation": validation,
    }
