from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from ssot_registry.model.enums import ASSURANCE_ENTITY_SECTIONS, ASSURANCE_ORIGINS, CLAIM_TIER_RANK, REF_FIELD_TARGETS
from ssot_registry.model.registry import normalize_repo_kind
from ssot_registry.util.errors import ValidationError
from ssot_registry.util.jsonio import stable_json_dumps

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
    "features": {"spec_ids", "claim_ids", "test_ids", "requires", "parent_feature_ids"},
    "profiles": {"feature_ids", "profile_ids"},
    "tests": {"feature_ids", "claim_ids", "evidence_ids"},
    "claims": {"feature_ids", "test_ids", "evidence_ids", "depends_on_claim_ids"},
    "evidence": {"claim_ids", "test_ids"},
    "issues": {"feature_ids", "claim_ids", "test_ids", "evidence_ids", "risk_ids"},
    "risks": {"feature_ids", "claim_ids", "test_ids", "evidence_ids", "issue_ids"},
    "boundaries": {"feature_ids", "profile_ids"},
    "releases": {"boundary_ids", "claim_ids", "evidence_ids"},
}

SECTIONS = tuple(SECTION_LABELS)
PARENT_AUDIT_TERMS = ("requires", "require", "required", "depends", "dependency", "prerequisite", "blocks", "blocked", "before")
PARENT_AUDIT_TARGET_HORIZONS = {"current", "explicit"}
PARENT_AUDIT_INCOMPLETE_STATUSES = {"absent", "partial"}


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


def _dedupe_sorted(values: list[str]) -> list[str]:
    return sorted(dict.fromkeys(values))


def _normalize_feature_parent_ids(row: dict[str, Any]) -> None:
    values = row.get("parent_feature_ids")
    if values is None:
        row["parent_feature_ids"] = []
        return
    if isinstance(values, list):
        row["parent_feature_ids"] = _dedupe_sorted(values)


def _repo_kind(registry: dict[str, Any]) -> str:
    repo = registry.get("repo")
    if isinstance(repo, dict):
        return normalize_repo_kind(repo.get("kind"))
    return "repo-local"


def _validate_assurance_origin_mutation(
    registry: dict[str, Any],
    section: str,
    row: dict[str, Any],
    *,
    current: dict[str, Any] | None = None,
) -> None:
    if section not in ASSURANCE_ENTITY_SECTIONS:
        return
    entity_id = row.get("id", current.get("id") if current else "<missing>")
    next_origin = row.get("origin", current.get("origin") if current else None)
    if next_origin not in ASSURANCE_ORIGINS:
        raise ValidationError(f"{SECTION_LABELS[section].title()} {entity_id} origin must be one of {sorted(ASSURANCE_ORIGINS)}")
    if _repo_kind(registry) == "repo-local" and next_origin == "ssot-core":
        raise ValidationError(
            f"{SECTION_LABELS[section].title()} {entity_id} cannot use origin ssot-core in a repo-local registry"
        )
    if current is not None:
        current_origin = current.get("origin")
        if current_origin in {"ssot-core", "ssot-origin", "extension-pack"} and next_origin != current_origin:
            raise ValidationError(
                f"{SECTION_LABELS[section].title()} {entity_id} origin cannot change from {current_origin} to {next_origin}"
            )


def _default_assurance_origin(registry: dict[str, Any]) -> str:
    repo_kind = _repo_kind(registry)
    if repo_kind in {"ssot-core", "ssot-origin", "extension-pack"}:
        return repo_kind
    return "repo-local"


def _ensure_assurance_origin(registry: dict[str, Any], section: str, row: dict[str, Any]) -> None:
    if section in ASSURANCE_ENTITY_SECTIONS:
        row.setdefault("origin", _default_assurance_origin(registry))


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
    from .config import run_repo_automation

    return {
        "validation": report,
        "automation": run_repo_automation(repo_root),
    }


def _safe_slug(entity_id: str) -> str:
    return entity_id.split(":", 1)[-1].replace("/", ".").replace(" ", "-").lower()


def _tier_sequence(target_tier: str) -> list[str]:
    if target_tier not in CLAIM_TIER_RANK:
        raise ValueError(f"Unsupported claim tier: {target_tier}")
    return [tier for tier, _rank in sorted(CLAIM_TIER_RANK.items(), key=lambda item: item[1]) if CLAIM_TIER_RANK[tier] <= CLAIM_TIER_RANK[target_tier]]


def _ensure_scaffold_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def create_feature_with_scaffolded_proof_graph(path: str | Path, row: dict[str, Any]) -> dict[str, Any]:
    registry_path, repo_root, registry = load_registry(path)
    entity_id = row.get("id")
    if not isinstance(entity_id, str):
        raise ValueError("feature row must include a string id")
    if entity_id in _row_lookup(registry, "features"):
        raise ValueError(f"Feature already exists: {entity_id}")

    candidate = deepcopy(row)
    _ensure_assurance_origin(registry, "features", candidate)
    candidate.setdefault("parent_feature_ids", [])
    _normalize_feature_parent_ids(candidate)
    for field_name in LINKABLE_FIELDS["features"]:
        if field_name in candidate and isinstance(candidate[field_name], list):
            candidate[field_name] = _dedupe_preserve(candidate[field_name])
    _validate_assurance_origin_mutation(registry, "features", candidate)

    plan = candidate.get("plan") if isinstance(candidate.get("plan"), dict) else {}
    target_tier = str(plan.get("target_claim_tier") or "T1")
    tiers = _tier_sequence(target_tier)
    slug = _safe_slug(entity_id)
    evidence_id = f"evd:{target_tier.lower()}.{slug}.proof-graph"
    evidence_path = f".ssot/evidence/{slug}/proof-graph-{target_tier.lower()}.json"
    claim_ids = [f"clm:{slug}.{tier.lower()}" for tier in tiers]
    test_ids = [f"tst:pytest.{slug}.{tier.lower()}.proof-graph" for tier in tiers]
    test_path_by_tier = {
        tier: f"tests/ssot_scaffold/test_{slug.replace('.', '_').replace('-', '_')}_{tier.lower()}_proof_graph.py"
        for tier in tiers
    }

    claims: list[dict[str, Any]] = []
    for index, tier in enumerate(tiers):
        claim_ids_in_chain = claim_ids[: index + 1]
        claim = {
            "id": claim_ids[index],
            "title": f"{candidate['title']} {tier} claim",
            "status": "declared" if tier == "T0" else "proposed",
            "tier": tier,
            "kind": "runtime",
            "description": f"{tier} scaffold claim for {entity_id}.",
            "origin": candidate["origin"],
            "feature_ids": [entity_id],
            "test_ids": [test_ids[index]],
            "evidence_ids": [evidence_id],
            "depends_on_claim_ids": claim_ids_in_chain[:-1],
        }
        claims.append(claim)

    test_rows: list[dict[str, Any]] = []
    for index, tier in enumerate(tiers):
        test_path = test_path_by_tier[tier]
        test_rows.append(
            {
                "id": test_ids[index],
                "title": f"{candidate['title']} {tier} proof-graph scaffold test",
                "body": f"Planned scaffold test for {entity_id} {tier} support.",
                "origin": candidate["origin"],
                "status": "planned",
                "kind": "pytest",
                "path": test_path,
                "feature_ids": [entity_id],
                "claim_ids": [claim_ids[index]],
                "evidence_ids": [evidence_id],
                "execution": {
                    "argv": ["python", "-m", "pytest", test_path, "-q"],
                    "cwd": ".",
                    "env": {},
                    "mode": "command",
                    "success": {"expected": 0, "type": "exit_code"},
                    "timeout_seconds": 600,
                },
            }
        )
    evidence_row = {
        "id": evidence_id,
        "title": f"{candidate['title']} proof-graph scaffold evidence",
        "status": "planned",
        "kind": "scaffold",
        "tier": target_tier,
        "body": f"Planned scaffold evidence for {entity_id}.",
        "origin": candidate["origin"],
        "path": evidence_path,
        "claim_ids": claim_ids,
        "test_ids": test_ids,
    }

    candidate["claim_ids"] = _dedupe_preserve([*claim_ids, *_ensure_list_field(candidate, "claim_ids")])
    candidate["test_ids"] = _dedupe_preserve([*test_ids, *_ensure_list_field(candidate, "test_ids")])
    registry["features"].append(candidate)
    registry.setdefault("claims", []).extend(claims)
    registry.setdefault("tests", []).extend(test_rows)
    registry.setdefault("evidence", []).append(evidence_row)

    for created in claims:
        _sync_reciprocals_for_row(registry, "claims", created)
    for created in test_rows:
        _sync_reciprocals_for_row(registry, "tests", created)
    _sync_reciprocals_for_row(registry, "evidence", evidence_row)
    _sync_reciprocals_for_row(registry, "features", candidate)

    for test_path in test_path_by_tier.values():
        _ensure_scaffold_file(
            repo_root / test_path,
            "def test_ssot_scaffold_placeholder():\n    assert True\n",
        )
    _ensure_scaffold_file(
        repo_root / evidence_path,
        stable_json_dumps(
            {
                "schema_version": "ssot.evidence.scaffold.v1",
                "feature_id": entity_id,
                "claim_ids": claim_ids,
                "test_ids": test_ids,
                "target_tier": target_tier,
                "status": "planned",
            }
        ),
    )

    mutation = _validate_and_save(registry_path, repo_root, registry, f"creating feature {entity_id} with scaffolded proof graph")
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "section": "features",
        "entity": candidate,
        "scaffolded": {
            "claim_ids": claim_ids,
            "test_id": test_ids[-1],
            "test_ids": test_ids,
            "evidence_id": evidence_id,
            "test_path": test_path_by_tier[tiers[-1]],
            "test_paths": [test_path_by_tier[tier] for tier in tiers],
            "evidence_path": evidence_path,
        },
        **mutation,
    }


def _rewrite_references_for_renamed_id(
    registry: dict[str, Any],
    *,
    target_section: str,
    old_id: str,
    new_id: str,
) -> None:
    for (source_section, field_name), ref_target_section in REF_FIELD_TARGETS.items():
        if ref_target_section != target_section:
            continue
        for source_row in registry.get(source_section, []):
            value = source_row.get(field_name)
            if field_name.endswith("_ids"):
                if not isinstance(value, list):
                    continue
                replaced = [new_id if item == old_id else item for item in value]
                source_row[field_name] = _dedupe_preserve(replaced)
                continue
            if value == old_id:
                source_row[field_name] = new_id

    program = registry.get("program", {})
    if target_section == "boundaries" and program.get("active_boundary_id") == old_id:
        program["active_boundary_id"] = new_id
    if target_section == "releases" and program.get("active_release_id") == old_id:
        program["active_release_id"] = new_id


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
    _ensure_assurance_origin(registry, section, candidate)
    if section == "claims":
        candidate.setdefault("depends_on_claim_ids", [])
    if section == "features":
        candidate.setdefault("parent_feature_ids", [])
        _normalize_feature_parent_ids(candidate)
    _validate_assurance_origin_mutation(registry, section, candidate)
    for field_name in LINKABLE_FIELDS[section]:
        if field_name in candidate and isinstance(candidate[field_name], list):
            candidate[field_name] = _dedupe_preserve(candidate[field_name])
    registry[section].append(candidate)
    _sync_reciprocals_for_row(registry, section, candidate)
    mutation = _validate_and_save(registry_path, repo_root, registry, f"creating {SECTION_LABELS[section]} {entity_id}")
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "section": section,
        "entity": candidate,
        **mutation,
    }


def get_entity(path: str | Path, section: str, entity_id: str) -> dict[str, Any]:
    _registry_path, _repo_root, registry = load_registry(path)
    return deepcopy(_entity_row(registry, section, entity_id))


def list_entities(path: str | Path, section: str, ids: list[str] | None = None, origin: str | None = None) -> list[dict[str, Any]]:
    _registry_path, _repo_root, registry = load_registry(path)
    if origin is not None and section not in ASSURANCE_ENTITY_SECTIONS:
        raise ValueError(f"Origin filtering is not supported for {SECTION_LABELS.get(section, section)} rows")
    if origin is not None and origin not in ASSURANCE_ORIGINS:
        raise ValueError(f"origin must be one of {', '.join(sorted(ASSURANCE_ORIGINS))}")
    if ids is None:
        rows = [deepcopy(row) for row in registry.get(section, [])]
        if origin is not None:
            rows = [row for row in rows if row.get("origin") == origin]
        return sorted(rows, key=lambda row: row["id"])

    lookup = _row_lookup(registry, section)
    requested_ids = _dedupe_preserve(ids)
    missing = sorted(entity_id for entity_id in requested_ids if entity_id not in lookup)
    if missing:
        label = SECTION_LABELS.get(section, section.rstrip("s"))
        raise ValueError(f"Unknown {label} ids: {', '.join(missing)}")
    rows = [deepcopy(lookup[entity_id]) for entity_id in requested_ids]
    if origin is not None:
        rows = [row for row in rows if row.get("origin") == origin]
    return sorted(rows, key=lambda row: row["id"])


def update_entity(path: str | Path, section: str, entity_id: str, changes: dict[str, Any]) -> dict[str, Any]:
    registry_path, repo_root, registry = load_registry(path)
    row = _entity_row(registry, section, entity_id)
    current_row = deepcopy(row)
    next_id = changes.get("id")
    if isinstance(next_id, str) and next_id != entity_id and next_id in _row_lookup(registry, section):
        raise ValueError(f"{SECTION_LABELS[section].title()} already exists: {next_id}")
    for field_name, value in changes.items():
        if value is None:
            continue
        row[field_name] = deepcopy(value)
    _validate_assurance_origin_mutation(registry, section, row, current=current_row)
    if section == "features":
        _normalize_feature_parent_ids(row)
    if isinstance(next_id, str) and next_id != entity_id:
        _rewrite_references_for_renamed_id(registry, target_section=section, old_id=entity_id, new_id=next_id)
        action = f"renaming {SECTION_LABELS[section]} {entity_id} to {next_id}"
    else:
        action = f"updating {SECTION_LABELS[section]} {entity_id}"
    mutation = _validate_and_save(registry_path, repo_root, registry, action)
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "section": section,
        "entity": deepcopy(row),
        **mutation,
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
    mutation = _validate_and_save(registry_path, repo_root, registry, f"deleting {SECTION_LABELS[section]} {entity_id}")
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "section": section,
        "deleted_id": entity_id,
        **mutation,
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
    if section == "features":
        _normalize_feature_parent_ids(row)
    mutation = _validate_and_save(registry_path, repo_root, registry, f"linking {SECTION_LABELS[section]} {entity_id}")
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "section": section,
        "entity": deepcopy(row),
        **mutation,
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
    if section == "features":
        _normalize_feature_parent_ids(row)
    mutation = _validate_and_save(registry_path, repo_root, registry, f"unlinking {SECTION_LABELS[section]} {entity_id}")
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "section": section,
        "entity": deepcopy(row),
        **mutation,
    }


def set_claim_status(path: str | Path, claim_id: str, status: str) -> dict[str, Any]:
    return update_entity(path, "claims", claim_id, {"status": status})


def set_feature_parents(path: str | Path, ids: list[str], parent_ids: list[str], mode: str) -> dict[str, Any]:
    if mode not in {"add", "set", "remove", "clear"}:
        raise ValueError("mode must be one of add, set, remove, or clear")
    registry_path, repo_root, registry = load_registry(path)
    feature_lookup = _row_lookup(registry, "features")
    target_ids = _dedupe_preserve(ids)
    requested_parent_ids = _dedupe_preserve(parent_ids)
    if mode == "clear":
        requested_parent_ids = []
    elif not requested_parent_ids:
        raise ValueError("At least one parent feature id is required")

    missing_targets = sorted(entity_id for entity_id in target_ids if entity_id not in feature_lookup)
    missing_parents = sorted(parent_id for parent_id in requested_parent_ids if parent_id not in feature_lookup)
    if missing_targets or missing_parents:
        messages: list[str] = []
        if missing_targets:
            messages.append(f"Unknown feature ids: {', '.join(missing_targets)}")
        if missing_parents:
            messages.append(f"Unknown parent feature ids: {', '.join(missing_parents)}")
        raise ValueError("; ".join(messages))

    for entity_id in target_ids:
        row = feature_lookup[entity_id]
        current = _ensure_list_field(row, "parent_feature_ids")
        if mode == "add":
            row["parent_feature_ids"] = _dedupe_sorted([*current, *requested_parent_ids])
        elif mode == "set":
            row["parent_feature_ids"] = _dedupe_sorted(requested_parent_ids)
        elif mode == "remove":
            removals = set(requested_parent_ids)
            row["parent_feature_ids"] = _dedupe_sorted([value for value in current if value not in removals])
        else:
            row["parent_feature_ids"] = []

    mutation = _validate_and_save(registry_path, repo_root, registry, f"{mode} feature parent links")
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "section": "features",
        "mode": mode,
        "ids": target_ids,
        "parent_ids": requested_parent_ids,
        "entities": [deepcopy(feature_lookup[entity_id]) for entity_id in target_ids],
        **mutation,
    }


def add_feature_children(path: str | Path, parent_id: str, child_ids: list[str]) -> dict[str, Any]:
    return set_feature_parents(path, child_ids, [parent_id], "add")


def remove_feature_children(path: str | Path, parent_id: str, child_ids: list[str]) -> dict[str, Any]:
    return set_feature_parents(path, child_ids, [parent_id], "remove")


def list_feature_children(path: str | Path, parent_id: str) -> list[dict[str, Any]]:
    _registry_path, _repo_root, registry = load_registry(path)
    feature_lookup = _row_lookup(registry, "features")
    if parent_id not in feature_lookup:
        raise ValueError(f"Unknown feature id: {parent_id}")
    rows = [
        deepcopy(row)
        for row in registry.get("features", [])
        if isinstance(row, dict) and parent_id in row.get("parent_feature_ids", [])
    ]
    return sorted(rows, key=lambda row: row["id"])


def _audit_text(row: dict[str, Any]) -> str:
    return " ".join(str(row.get(field_name, "")) for field_name in ("id", "title", "description", "body")).lower()


def audit_feature_parent_links(path: str | Path) -> dict[str, Any]:
    registry_path, _repo_root, registry = load_registry(path)
    feature_lookup = _row_lookup(registry, "features")
    findings: list[dict[str, Any]] = []

    for feature in sorted(feature_lookup.values(), key=lambda row: row["id"]):
        feature_id = str(feature["id"])
        parent_ids = feature.get("parent_feature_ids", [])
        if not isinstance(parent_ids, list):
            continue
        for parent_id in sorted(dict.fromkeys(parent_ids)):
            parent = feature_lookup.get(parent_id)
            if parent is None:
                continue

            reasons: list[str] = []
            feature_horizon = feature.get("plan", {}).get("horizon") if isinstance(feature.get("plan"), dict) else None
            parent_status = parent.get("implementation_status")
            if (feature_horizon in PARENT_AUDIT_TARGET_HORIZONS or feature.get("implementation_status") == "implemented") and (
                parent_status in PARENT_AUDIT_INCOMPLETE_STATUSES
            ):
                reasons.append("targeted_or_implemented_child_has_incomplete_parent")

            combined_text = f"{_audit_text(feature)} {_audit_text(parent)}"
            matched_terms = [term for term in PARENT_AUDIT_TERMS if term in combined_text]
            if matched_terms:
                reasons.append(f"dependency_language:{','.join(matched_terms)}")

            if not reasons:
                continue

            confidence = "high" if len(reasons) > 1 else "medium"
            if reasons == [reason for reason in reasons if reason.startswith("dependency_language:")]:
                confidence = "low"
            findings.append(
                {
                    "feature_id": feature_id,
                    "parent_feature_id": parent_id,
                    "reason": reasons,
                    "suggested_requires_edge": {"feature_id": feature_id, "requires": parent_id},
                    "confidence": confidence,
                }
            )

    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "findings": findings,
        "summary": {
            "finding_count": len(findings),
            "high_confidence_count": sum(1 for finding in findings if finding["confidence"] == "high"),
            "medium_confidence_count": sum(1 for finding in findings if finding["confidence"] == "medium"),
            "low_confidence_count": sum(1 for finding in findings if finding["confidence"] == "low"),
        },
    }


def migrate_feature_parent_audit_edge(
    path: str | Path,
    feature_id: str,
    parent_id: str,
    *,
    remove_parent_link: bool = False,
) -> dict[str, Any]:
    registry_path, repo_root, registry = load_registry(path)
    feature_lookup = _row_lookup(registry, "features")
    if feature_id not in feature_lookup:
        raise ValueError(f"Unknown feature id: {feature_id}")
    if parent_id not in feature_lookup:
        raise ValueError(f"Unknown parent feature id: {parent_id}")

    feature = feature_lookup[feature_id]
    parent_ids = _ensure_list_field(feature, "parent_feature_ids")
    if parent_id not in parent_ids:
        raise ValueError(f"Feature {feature_id} does not have parent link {parent_id}")

    requires = _ensure_list_field(feature, "requires")
    added_requires = parent_id not in requires
    if added_requires:
        requires.append(parent_id)
        feature["requires"] = _dedupe_preserve(requires)

    removed_parent_link = False
    if remove_parent_link:
        feature["parent_feature_ids"] = _dedupe_sorted([value for value in parent_ids if value != parent_id])
        removed_parent_link = True
    else:
        _normalize_feature_parent_ids(feature)

    mutation = _validate_and_save(registry_path, repo_root, registry, "migrating feature parent audit edge")
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "feature_id": feature_id,
        "parent_feature_id": parent_id,
        "added_requires": added_requires,
        "removed_parent_link": removed_parent_link,
        "entity": deepcopy(feature),
        **mutation,
    }


def set_claim_tier(path: str | Path, claim_id: str, tier: str) -> dict[str, Any]:
    registry_path, repo_root, registry = load_registry(path)
    row = _entity_row(registry, "claims", claim_id)
    current_tier = row.get("tier")
    if current_tier == tier:
        report = validate_registry_document(registry, registry_path, repo_root)
        if not report["passed"]:
            detail = "; ".join(report["failures"])
            raise ValidationError(f"Registry validation failed while checking claim {claim_id}: {detail}")
        return {
            "passed": True,
            "registry_path": registry_path.as_posix(),
            "section": "claims",
            "entity": deepcopy(row),
            "changed": False,
            "message": f"Claim {claim_id} is already tier {tier}; no in-place tier mutation was performed.",
            "validation": report,
        }
    raise ValidationError(
        f"Claim {claim_id} tier is immutable. Create a new claim row at tier {tier} and link the existing claim through depends_on_claim_ids."
    )


def set_issue_status(path: str | Path, issue_id: str, status: str) -> dict[str, Any]:
    return update_entity(path, "issues", issue_id, {"status": status})


def set_risk_status(path: str | Path, risk_id: str, status: str) -> dict[str, Any]:
    return update_entity(path, "risks", risk_id, {"status": status})


def add_boundary_features(path: str | Path, boundary_id: str, feature_ids: list[str]) -> dict[str, Any]:
    return link_entities(path, "boundaries", boundary_id, {"feature_ids": feature_ids})


def remove_boundary_features(path: str | Path, boundary_id: str, feature_ids: list[str]) -> dict[str, Any]:
    return unlink_entities(path, "boundaries", boundary_id, {"feature_ids": feature_ids})


def add_boundary_profiles(path: str | Path, boundary_id: str, profile_ids: list[str]) -> dict[str, Any]:
    return link_entities(path, "boundaries", boundary_id, {"profile_ids": profile_ids})


def remove_boundary_profiles(path: str | Path, boundary_id: str, profile_ids: list[str]) -> dict[str, Any]:
    return unlink_entities(path, "boundaries", boundary_id, {"profile_ids": profile_ids})


def add_release_claims(path: str | Path, release_id: str, claim_ids: list[str]) -> dict[str, Any]:
    return link_entities(path, "releases", release_id, {"claim_ids": claim_ids})


def remove_release_claims(path: str | Path, release_id: str, claim_ids: list[str]) -> dict[str, Any]:
    return unlink_entities(path, "releases", release_id, {"claim_ids": claim_ids})


def add_release_evidence(path: str | Path, release_id: str, evidence_ids: list[str]) -> dict[str, Any]:
    return link_entities(path, "releases", release_id, {"evidence_ids": evidence_ids})


def remove_release_evidence(path: str | Path, release_id: str, evidence_ids: list[str]) -> dict[str, Any]:
    return unlink_entities(path, "releases", release_id, {"evidence_ids": evidence_ids})


def add_release_boundaries(path: str | Path, release_id: str, boundary_ids: list[str]) -> dict[str, Any]:
    _registry_path, _repo_root, registry = load_registry(path)
    release = _entity_row(registry, "releases", release_id)
    primary_boundary_id = release.get("boundary_id")
    if isinstance(primary_boundary_id, str):
        boundary_ids = [primary_boundary_id, *boundary_ids]
    return link_entities(path, "releases", release_id, {"boundary_ids": boundary_ids})


def remove_release_boundaries(path: str | Path, release_id: str, boundary_ids: list[str]) -> dict[str, Any]:
    _registry_path, _repo_root, registry = load_registry(path)
    release = _entity_row(registry, "releases", release_id)
    if release.get("boundary_id") in set(boundary_ids):
        raise ValueError("Cannot remove the primary boundary_id from release boundary_ids; update the release boundary_id first")
    return unlink_entities(path, "releases", release_id, {"boundary_ids": boundary_ids})
