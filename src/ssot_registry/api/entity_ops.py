from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from ssot_registry.model.enums import REF_FIELD_TARGETS
from ssot_registry.util.errors import ValidationError

from .load import load_registry
from .save import save_registry
from .validate import validate_registry_document

SECTION_LABELS = {
    "features": "feature",
    "profiles": "profile",
    "tests": "test",
    "claims": "claim",
    "evidence": "evidence",
    "issues": "issue",
    "risks": "risk",
    "boundaries": "boundary",
    "releases": "release",
}

RECIPROCAL_FIELDS = {
    ("features", "claim_ids"): ("claims", "feature_ids"),
    ("features", "test_ids"): ("tests", "feature_ids"),
    ("tests", "feature_ids"): ("features", "test_ids"),
    ("tests", "claim_ids"): ("claims", "test_ids"),
    ("tests", "evidence_ids"): ("evidence", "test_ids"),
    ("claims", "feature_ids"): ("features", "claim_ids"),
    ("claims", "test_ids"): ("tests", "claim_ids"),
    ("claims", "evidence_ids"): ("evidence", "claim_ids"),
    ("evidence", "claim_ids"): ("claims", "evidence_ids"),
    ("evidence", "test_ids"): ("tests", "evidence_ids"),
    ("issues", "risk_ids"): ("risks", "issue_ids"),
    ("risks", "issue_ids"): ("issues", "risk_ids"),
}

LINKABLE_FIELDS = {
    "features": {"claim_ids", "test_ids", "requires"},
    "tests": {"feature_ids", "claim_ids", "evidence_ids"},
    "claims": {"feature_ids", "test_ids", "evidence_ids"},
    "evidence": {"claim_ids", "test_ids"},
    "issues": {"feature_ids", "claim_ids", "test_ids", "evidence_ids", "risk_ids"},
    "risks": {"feature_ids", "claim_ids", "test_ids", "evidence_ids", "issue_ids"},
    "profiles": {"feature_ids", "profile_ids"},
    "boundaries": {"feature_ids", "profile_ids"},
    "releases": {"claim_ids", "evidence_ids"},
}

SECTIONS = tuple(SECTION_LABELS)


def _row_lookup(registry: dict[str, Any], section: str) -> dict[str, dict[str, Any]]:
    return {row["id"]: row for row in registry.get(section, []) if isinstance(row, dict) and isinstance(row.get("id"), str)}


def _entity_row(registry: dict[str, Any], section: str, entity_id: str) -> dict[str, Any]:
    lookup = _row_lookup(registry, section)
    try:
        return lookup[entity_id]
    except KeyError as exc:
        raise ValueError(f"Unknown {SECTION_LABELS[section]} id: {entity_id}") from exc


def _dedupe_preserve(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def _ensure_list_field(row: dict[str, Any], field_name: str) -> list[str]:
    values = row.get(field_name)
    if not isinstance(values, list):
        values = []
        row[field_name] = values
    return values


def _apply_reciprocal_add(registry: dict[str, Any], section: str, field_name: str, entity_id: str, target_id: str) -> None:
    reciprocal = RECIPROCAL_FIELDS.get((section, field_name))
    if reciprocal is None:
        return
    target_section, target_field = reciprocal
    target_lookup = _row_lookup(registry, target_section)
    target_row = target_lookup.get(target_id)
    if target_row is None:
        return
    target_values = _ensure_list_field(target_row, target_field)
    if entity_id not in target_values:
        target_values.append(entity_id)
        target_row[target_field] = _dedupe_preserve(target_values)


def _apply_reciprocal_remove(registry: dict[str, Any], section: str, field_name: str, entity_id: str, target_id: str) -> None:
    reciprocal = RECIPROCAL_FIELDS.get((section, field_name))
    if reciprocal is None:
        return
    target_section, target_field = reciprocal
    target_lookup = _row_lookup(registry, target_section)
    target_row = target_lookup.get(target_id)
    if target_row is None:
        return
    target_values = _ensure_list_field(target_row, target_field)
    target_row[target_field] = [value for value in target_values if value != entity_id]


def _sync_reciprocals_for_row(registry: dict[str, Any], section: str, row: dict[str, Any]) -> None:
    entity_id = row["id"]
    for field_name in LINKABLE_FIELDS[section]:
        values = row.get(field_name)
        if isinstance(values, list):
            for target_id in values:
                _apply_reciprocal_add(registry, section, field_name, entity_id, target_id)


def _validate_and_save(registry_path: Path, repo_root: Path, registry: dict[str, Any], action: str) -> dict[str, Any]:
    report = validate_registry_document(registry, registry_path, repo_root)
    if not report["passed"]:
        detail = "; ".join(report["failures"])
        raise ValidationError(f"Registry validation failed after {action}: {detail}")
    save_registry(registry_path, registry)
    return report


def create_entity(path: str | Path, section: str, row: dict[str, Any]) -> dict[str, Any]:
    registry_path, repo_root, registry = load_registry(path)
    if section not in SECTIONS:
        raise ValueError(f"Unsupported section: {section}")
    entity_id = row.get("id")
    if not isinstance(entity_id, str):
        raise ValueError(f"{SECTION_LABELS[section]} row must include a string id")
    if entity_id in _row_lookup(registry, section):
        raise ValueError(f"{SECTION_LABELS[section].title()} already exists: {entity_id}")

    candidate = deepcopy(row)
    for field_name in LINKABLE_FIELDS[section]:
        if field_name in candidate and isinstance(candidate[field_name], list):
            candidate[field_name] = _dedupe_preserve(candidate[field_name])
    registry[section].append(candidate)
    _sync_reciprocals_for_row(registry, section, candidate)
    _validate_and_save(registry_path, repo_root, registry, f"creating {SECTION_LABELS[section]} {entity_id}")
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "section": section,
        "entity": candidate,
    }


def get_entity(path: str | Path, section: str, entity_id: str) -> dict[str, Any]:
    registry_path, _repo_root, registry = load_registry(path)
    row = deepcopy(_entity_row(registry, section, entity_id))
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "section": section,
        "entity": row,
    }


def list_entities(path: str | Path, section: str) -> dict[str, Any]:
    registry_path, _repo_root, registry = load_registry(path)
    rows = sorted((deepcopy(row) for row in registry.get(section, [])), key=lambda row: row["id"])
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "section": section,
        "count": len(rows),
        "entities": rows,
    }


def update_entity(path: str | Path, section: str, entity_id: str, changes: dict[str, Any]) -> dict[str, Any]:
    registry_path, repo_root, registry = load_registry(path)
    row = _entity_row(registry, section, entity_id)
    for field_name, value in changes.items():
        if value is None:
            continue
        row[field_name] = deepcopy(value)
    _validate_and_save(registry_path, repo_root, registry, f"updating {SECTION_LABELS[section]} {entity_id}")
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "section": section,
        "entity": deepcopy(row),
    }


def _find_incoming_references(registry: dict[str, Any], section: str, entity_id: str) -> tuple[list[tuple[str, str, str]], list[str]]:
    auto_clean: list[tuple[str, str, str]] = []
    blocking: list[str] = []
    for (source_section, field_name), target_section in REF_FIELD_TARGETS.items():
        if target_section != section:
            continue
        reciprocal = RECIPROCAL_FIELDS.get((source_section, field_name))
        can_auto_clean = reciprocal is not None and reciprocal[0] == section
        for row in registry.get(source_section, []):
            source_id = row.get("id", "<missing>")
            value = row.get(field_name)
            if field_name.endswith("_ids"):
                if isinstance(value, list) and entity_id in value:
                    if can_auto_clean:
                        auto_clean.append((source_section, source_id, field_name))
                    else:
                        blocking.append(f"{source_section}.{source_id}.{field_name}")
            elif value == entity_id:
                blocking.append(f"{source_section}.{source_id}.{field_name}")

    program = registry.get("program", {})
    if section == "boundaries" and program.get("active_boundary_id") == entity_id:
        blocking.append("program.active_boundary_id")
    if section == "releases" and program.get("active_release_id") == entity_id:
        blocking.append("program.active_release_id")
    return auto_clean, sorted(set(blocking))


def delete_entity(path: str | Path, section: str, entity_id: str) -> dict[str, Any]:
    registry_path, repo_root, registry = load_registry(path)
    _entity_row(registry, section, entity_id)
    auto_clean, refs = _find_incoming_references(registry, section, entity_id)
    if refs:
        raise ValidationError(
            f"Cannot delete {SECTION_LABELS[section]} {entity_id}; it is still referenced by: {', '.join(refs)}"
        )

    for source_section, source_id, field_name in auto_clean:
        source_row = _entity_row(registry, source_section, source_id)
        values = _ensure_list_field(source_row, field_name)
        source_row[field_name] = [value for value in values if value != entity_id]

    rows = registry.get(section, [])
    registry[section] = [row for row in rows if row.get("id") != entity_id]
    _validate_and_save(registry_path, repo_root, registry, f"deleting {SECTION_LABELS[section]} {entity_id}")
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "section": section,
        "deleted_id": entity_id,
    }


def link_entities(path: str | Path, section: str, entity_id: str, links: dict[str, list[str]]) -> dict[str, Any]:
    registry_path, repo_root, registry = load_registry(path)
    row = _entity_row(registry, section, entity_id)
    for field_name, target_ids in links.items():
        if field_name not in LINKABLE_FIELDS[section]:
            raise ValueError(f"Field {field_name} is not linkable for {SECTION_LABELS[section]}")
        values = _ensure_list_field(row, field_name)
        for target_id in target_ids:
            if target_id not in values:
                values.append(target_id)
                _apply_reciprocal_add(registry, section, field_name, entity_id, target_id)
        row[field_name] = _dedupe_preserve(values)
    _validate_and_save(registry_path, repo_root, registry, f"linking {SECTION_LABELS[section]} {entity_id}")
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "section": section,
        "entity": deepcopy(row),
    }


def unlink_entities(path: str | Path, section: str, entity_id: str, links: dict[str, list[str]]) -> dict[str, Any]:
    registry_path, repo_root, registry = load_registry(path)
    row = _entity_row(registry, section, entity_id)
    for field_name, target_ids in links.items():
        if field_name not in LINKABLE_FIELDS[section]:
            raise ValueError(f"Field {field_name} is not linkable for {SECTION_LABELS[section]}")
        values = _ensure_list_field(row, field_name)
        for target_id in target_ids:
            if target_id in values:
                values.remove(target_id)
            _apply_reciprocal_remove(registry, section, field_name, entity_id, target_id)
        row[field_name] = _dedupe_preserve(values)
    _validate_and_save(registry_path, repo_root, registry, f"unlinking {SECTION_LABELS[section]} {entity_id}")
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "section": section,
        "entity": deepcopy(row),
    }


def set_claim_status(path: str | Path, claim_id: str, status: str) -> dict[str, Any]:
    return update_entity(path, "claims", claim_id, {"status": status})


def set_claim_tier(path: str | Path, claim_id: str, tier: str) -> dict[str, Any]:
    return update_entity(path, "claims", claim_id, {"tier": tier})


def set_issue_status(path: str | Path, issue_id: str, status: str) -> dict[str, Any]:
    return update_entity(path, "issues", issue_id, {"status": status})


def set_risk_status(path: str | Path, risk_id: str, status: str) -> dict[str, Any]:
    return update_entity(path, "risks", risk_id, {"status": status})


def add_boundary_features(path: str | Path, boundary_id: str, feature_ids: list[str]) -> dict[str, Any]:
    return link_entities(path, "boundaries", boundary_id, {"feature_ids": feature_ids})


def remove_boundary_features(path: str | Path, boundary_id: str, feature_ids: list[str]) -> dict[str, Any]:
    return unlink_entities(path, "boundaries", boundary_id, {"feature_ids": feature_ids})


def add_release_claims(path: str | Path, release_id: str, claim_ids: list[str]) -> dict[str, Any]:
    return link_entities(path, "releases", release_id, {"claim_ids": claim_ids})


def remove_release_claims(path: str | Path, release_id: str, claim_ids: list[str]) -> dict[str, Any]:
    return unlink_entities(path, "releases", release_id, {"claim_ids": claim_ids})


def add_release_evidence(path: str | Path, release_id: str, evidence_ids: list[str]) -> dict[str, Any]:
    return link_entities(path, "releases", release_id, {"evidence_ids": evidence_ids})


def remove_release_evidence(path: str | Path, release_id: str, evidence_ids: list[str]) -> dict[str, Any]:
    return unlink_entities(path, "releases", release_id, {"evidence_ids": evidence_ids})


def add_boundary_profiles(path: str | Path, boundary_id: str, profile_ids: list[str]) -> dict[str, Any]:
    return link_entities(path, "boundaries", boundary_id, {"profile_ids": profile_ids})


def remove_boundary_profiles(path: str | Path, boundary_id: str, profile_ids: list[str]) -> dict[str, Any]:
    return unlink_entities(path, "boundaries", boundary_id, {"profile_ids": profile_ids})
