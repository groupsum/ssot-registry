from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ssot_contracts.generated.python.tui_metadata import ENTITY_VIEW_SECTIONS


SECTION_TO_COMMAND = {
    "features": "feature",
    "profiles": "profile",
    "tests": "test",
    "claims": "claim",
    "evidence": "evidence",
    "issues": "issue",
    "risks": "risk",
    "boundaries": "boundary",
    "releases": "release",
    "adrs": "adr",
    "specs": "spec",
}


@dataclass(frozen=True, slots=True)
class SectionPresentationSpec:
    section: str
    label: str
    command_name: str
    preferred_columns: tuple[str, ...]
    detail_primary_fields: tuple[str, ...]
    detail_badge_fields: tuple[str, ...]
    relation_fields: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EntityRowViewModel:
    entity_id: str
    cells: dict[str, str]
    raw_entity: dict[str, Any]


@dataclass(frozen=True, slots=True)
class DetailFieldViewModel:
    label: str
    value: str


@dataclass(frozen=True, slots=True)
class RelatedResourceViewModel:
    kind: str
    value: str
    label: str
    field_path: str
    section: str | None = None
    absolute_path: str | None = None


@dataclass(frozen=True, slots=True)
class EntityDetailViewModel:
    title: str
    subtitle: str
    badges: list[str] = field(default_factory=list)
    primary_fields: list[DetailFieldViewModel] = field(default_factory=list)
    secondary_fields: list[DetailFieldViewModel] = field(default_factory=list)
    resources: list[RelatedResourceViewModel] = field(default_factory=list)
    raw_json: str = ""


def build_section_specs(entity_sections: tuple[tuple[str, str], ...]) -> dict[str, SectionPresentationSpec]:
    specs: dict[str, SectionPresentationSpec] = {}
    for section, label in entity_sections:
        preferred_columns = ENTITY_VIEW_SECTIONS.get(section, ("id", "title", "status"))
        specs[section] = SectionPresentationSpec(
            section=section,
            label=label,
            command_name=SECTION_TO_COMMAND.get(section, section.rstrip("s")),
            preferred_columns=preferred_columns,
            detail_primary_fields=_preferred_primary_fields(section),
            detail_badge_fields=("status", "implementation_status", "origin", "kind", "tier"),
            relation_fields=_preferred_relation_fields(section),
        )
    return specs


def build_row_view_models(columns: list[str], rows: list[dict[str, Any]]) -> list[EntityRowViewModel]:
    view_models: list[EntityRowViewModel] = []
    for row in rows:
        entity_id = str(row.get("id", ""))
        cells = {column: _stringify_value(row.get(column, "")) for column in columns}
        view_models.append(EntityRowViewModel(entity_id=entity_id, cells=cells, raw_entity=row))
    return view_models


def build_detail_view_model(
    entity: dict[str, Any],
    spec: SectionPresentationSpec,
    *,
    workspace_root: str | Path | None,
    entity_index: dict[str, tuple[str, dict[str, Any]]],
) -> EntityDetailViewModel:
    title = str(entity.get("title") or entity.get("version") or entity.get("id") or "<unnamed>")
    subtitle = str(entity.get("id") or spec.label)
    badges = [f"{field}: {_stringify_value(entity[field])}" for field in spec.detail_badge_fields if field in entity]
    primary_fields = [
        DetailFieldViewModel(label=field.replace("_", " ").title(), value=_stringify_value(entity.get(field, "")))
        for field in spec.detail_primary_fields
        if field in entity
    ]
    secondary_fields = [
        DetailFieldViewModel(label=key.replace("_", " ").title(), value=_stringify_value(value))
        for key, value in entity.items()
        if key not in set(spec.detail_primary_fields) | set(spec.detail_badge_fields)
    ]
    resources = _build_resources(entity, workspace_root=workspace_root, entity_index=entity_index)
    return EntityDetailViewModel(
        title=title,
        subtitle=subtitle,
        badges=badges,
        primary_fields=primary_fields,
        secondary_fields=secondary_fields,
        resources=resources,
        raw_json=json.dumps(entity, indent=2, sort_keys=True),
    )


def render_structured_detail(view_model: EntityDetailViewModel) -> str:
    lines = [view_model.title, view_model.subtitle]
    if view_model.badges:
        lines.extend(["", "Badges", *[f"- {badge}" for badge in view_model.badges]])
    if view_model.primary_fields:
        lines.extend(["", "Primary"])
        for field in view_model.primary_fields:
            _append_field(lines, field)
    if view_model.secondary_fields:
        lines.extend(["", "Details"])
        for field in view_model.secondary_fields[:12]:
            _append_field(lines, field)
        if len(view_model.secondary_fields) > 12:
            lines.append(f"- ... {len(view_model.secondary_fields) - 12} more fields")
    if view_model.resources:
        lines.extend(["", "Related"])
        lines.extend(f"- {resource.kind}: {resource.field_path} -> {resource.label}" for resource in view_model.resources)
    return "\n".join(lines)


def _append_field(lines: list[str], field: DetailFieldViewModel) -> None:
    if "\n" not in field.value:
        lines.append(f"- {field.label}: {field.value}")
        return
    lines.append(f"- {field.label}:")
    for line in field.value.splitlines():
        lines.append(f"  {line}" if line else "  ")


def _preferred_primary_fields(section: str) -> tuple[str, ...]:
    defaults = {
        "features": ("id", "title", "implementation_status", "summary"),
        "profiles": ("id", "title", "status", "claim_tier"),
        "tests": ("id", "title", "status", "path"),
        "claims": ("id", "title", "status", "tier"),
        "evidence": ("id", "title", "status", "path"),
        "issues": ("id", "title", "status", "horizon"),
        "risks": ("id", "title", "status", "severity"),
        "boundaries": ("id", "title", "status"),
        "releases": ("id", "version", "status", "boundary_id"),
        "adrs": ("id", "summary", "path"),
        "specs": ("id", "summary", "path"),
    }
    return defaults.get(section, ("id", "title", "status"))


def _preferred_relation_fields(section: str) -> tuple[str, ...]:
    defaults = {
        "features": ("claim_ids", "test_ids", "requires"),
        "profiles": ("feature_ids", "profile_ids"),
        "tests": ("feature_ids", "claim_ids", "evidence_ids", "path"),
        "claims": ("feature_ids", "test_ids", "evidence_ids"),
        "evidence": ("claim_ids", "test_ids", "path"),
        "issues": ("feature_ids", "claim_ids", "test_ids", "evidence_ids", "risk_ids"),
        "risks": ("feature_ids", "claim_ids", "test_ids", "evidence_ids", "issue_ids"),
        "boundaries": ("feature_ids", "profile_ids"),
        "releases": ("claim_ids", "evidence_ids", "boundary_id"),
        "adrs": ("path", "supersedes", "superseded_by"),
        "specs": ("path", "supersedes", "superseded_by"),
    }
    return defaults.get(section, tuple())


def _build_resources(
    entity: dict[str, Any],
    *,
    workspace_root: str | Path | None,
    entity_index: dict[str, tuple[str, dict[str, Any]]],
) -> list[RelatedResourceViewModel]:
    root = Path(workspace_root) if workspace_root is not None else None
    resources: list[RelatedResourceViewModel] = []
    seen: set[tuple[str, str]] = set()

    def walk(value: Any, field_path: str) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                nested_path = f"{field_path}.{key}" if field_path else key
                walk(nested, nested_path)
            return
        if isinstance(value, list):
            for index, nested in enumerate(value):
                walk(nested, f"{field_path}[{index}]")
            return
        if not isinstance(value, str):
            return
        if value in entity_index:
            section, row = entity_index[value]
            token = ("entity", value)
            if token not in seen:
                seen.add(token)
                resources.append(
                    RelatedResourceViewModel(
                        kind="entity",
                        value=value,
                        label=str(row.get("title") or row.get("version") or value),
                        field_path=field_path,
                        section=section,
                    )
                )
            return
        if root is not None and field_path.split(".")[-1] == "path":
            absolute_path = root / value
            if absolute_path.exists():
                token = ("file", absolute_path.as_posix())
                if token not in seen:
                    seen.add(token)
                    resources.append(
                        RelatedResourceViewModel(
                            kind="file",
                            value=value,
                            label=value,
                            field_path=field_path,
                            absolute_path=absolute_path.as_posix(),
                        )
                    )

    walk(entity, "")
    return resources


def _stringify_value(value: object) -> str:
    if isinstance(value, list):
        return ", ".join(_stringify_value(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return str(value)
