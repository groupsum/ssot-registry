from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from ssot_registry.model.document import (
    build_document_path,
    default_document_id_reservations,
    load_document_manifest,
    normalize_document_id,
    parse_document_filename,
)
from ssot_registry.model.enums import SCHEMA_VERSION
from ssot_registry.util.errors import RegistryError, ValidationError
from ssot_registry.util.fs import sha256_normalized_text_path
from ssot_registry.util.jsonio import save_json
from ssot_registry.version import __version__

from .documents import sync_documents_in_memory
from .load import load_registry
from .save import save_registry
from .validate import validate_registry_document


LEGACY_V3_VERSION = "0.1.2"
SSOT_ORIGIN_V8_OFFSET = 599


def _extract_title(kind: str, path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return path.stem
    first = lines[0].strip()
    if kind == "adr" and first.startswith("# ADR-") and ":" in first:
        return first.split(":", 1)[1].strip()
    if first.startswith("#"):
        return first.lstrip("#").strip()
    return path.stem


def _rename_legacy_packaged_specs(registry: dict[str, Any], repo_root: Path) -> list[dict[str, str]]:
    renames: list[dict[str, str]] = []
    spec_root = repo_root / registry["paths"]["spec_root"]
    if not spec_root.exists():
        return renames

    for entry in load_document_manifest("spec"):
        legacy = spec_root / f"{entry['slug']}.md"
        target = repo_root / entry["target_path"]
        if not legacy.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            legacy.rename(target)
            renames.append({"from": legacy.relative_to(repo_root).as_posix(), "to": target.relative_to(repo_root).as_posix()})
        else:
            legacy.unlink()
            renames.append({"from": legacy.relative_to(repo_root).as_posix(), "to": target.relative_to(repo_root).as_posix()})
    return renames


def _remove_legacy_numbered_packaged_docs(registry: dict[str, Any], repo_root: Path, kind: str) -> list[str]:
    removed: list[str] = []
    document_root = repo_root / registry["paths"]["adr_root" if kind == "adr" else "spec_root"]
    if not document_root.exists():
        return removed

    prefix = "ADR" if kind == "adr" else "SPEC"
    for entry in load_document_manifest(kind):
        legacy_number = entry["number"] - SSOT_ORIGIN_V8_OFFSET
        if legacy_number < 1:
            continue
        legacy = document_root / f"{prefix}-{legacy_number:04d}-{entry['slug']}.md"
        if legacy.exists():
            legacy.unlink()
            removed.append(legacy.relative_to(repo_root).as_posix())
    return removed


def _seed_tooling_v4(registry: dict[str, Any], *, previous_version: str, target_version: str) -> None:
    registry["schema_version"] = 4
    registry["tooling"] = {
        "ssot_registry_version": target_version,
        "initialized_with_version": previous_version,
        "last_upgraded_from_version": previous_version,
    }
    registry["document_id_reservations"] = default_document_id_reservations()
    registry.setdefault("adrs", [])
    registry.setdefault("specs", [])


def _collect_repo_local_documents(registry: dict[str, Any], repo_root: Path, kind: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    manifest_paths = {entry["target_path"] for entry in load_document_manifest(kind)}
    section = "adrs" if kind == "adr" else "specs"
    existing_numbers = {
        row["number"] for row in registry.get(section, []) if isinstance(row, dict) and isinstance(row.get("number"), int)
    }
    existing_ids = {
        row["id"] for row in registry.get(section, []) if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    document_root = repo_root / registry["paths"]["adr_root" if kind == "adr" else "spec_root"]
    if not document_root.exists():
        return rows

    for path in sorted(document_root.glob("*.md")):
        relative_path = path.relative_to(repo_root).as_posix()
        if relative_path in manifest_paths:
            continue
        parsed = parse_document_filename(kind, path.name)
        if parsed is None:
            raise ValidationError(
                f"Cannot migrate {relative_path}; filename must match {'ADR' if kind == 'adr' else 'SPEC'}-NNNN-slug.md"
            )
        number, slug = parsed
        if number < 1000:
            raise ValidationError(f"Cannot migrate {relative_path}; repo-local {kind} numbers must be >= 1000")
        document_id = normalize_document_id(kind, number)
        if number in existing_numbers or document_id in existing_ids:
            raise ValidationError(f"Cannot migrate {relative_path}; number {number} conflicts with an existing {kind}")

        row = {
            "id": document_id,
            "number": number,
            "slug": slug,
            "title": _extract_title(kind, path),
            "path": build_document_path(registry["paths"], kind, number, slug),
            "origin": "repo-local",
            "managed": False,
            "immutable": False,
            "package_version": target_version_from_registry(registry),
            "content_sha256": sha256_normalized_text_path(path),
        }
        if kind == "adr":
            row["status"] = "draft"
            row["supersedes"] = []
            row["superseded_by"] = []
            row["status_notes"] = []
        else:
            row["kind"] = "local-policy"
            row["status"] = "draft"
            row["supersedes"] = []
            row["superseded_by"] = []
            row["status_notes"] = []
        rows.append(row)
        existing_numbers.add(number)
        existing_ids.add(document_id)

    return rows


def migrate_v3_to_v4(registry: dict[str, Any], repo_root: Path, *, previous_version: str, target_version: str) -> dict[str, Any]:
    migrated = deepcopy(registry)
    _seed_tooling_v4(migrated, previous_version=previous_version, target_version=target_version)
    _rename_legacy_packaged_specs(migrated, repo_root)
    _remove_legacy_numbered_packaged_docs(migrated, repo_root, "adr")
    _remove_legacy_numbered_packaged_docs(migrated, repo_root, "spec")
    migrated["adrs"] = []
    migrated["specs"] = []
    sync_documents_in_memory(migrated, repo_root, "adr")
    sync_documents_in_memory(migrated, repo_root, "spec")
    migrated["adrs"].extend(_collect_repo_local_documents(migrated, repo_root, "adr"))
    migrated["specs"].extend(_collect_repo_local_documents(migrated, repo_root, "spec"))
    migrated["adrs"] = sorted(migrated["adrs"], key=lambda row: (row["number"], row["id"]))
    migrated["specs"] = sorted(migrated["specs"], key=lambda row: (row["number"], row["id"]))
    return migrated


def _seed_v5_profiles(registry: dict[str, Any]) -> None:
    registry["schema_version"] = 5
    registry.setdefault("profiles", [])
    for boundary in registry.get("boundaries", []):
        boundary.setdefault("profile_ids", [])


def migrate_v4_to_v5(
    registry: dict[str, Any],
    repo_root: Path,
    *,
    previous_version: str,
    target_version: str,
) -> dict[str, Any]:
    _ = repo_root, previous_version, target_version
    migrated = deepcopy(registry)
    _seed_v5_profiles(migrated)
    return migrated


def migrate_v5_to_v6(
    registry: dict[str, Any],
    repo_root: Path,
    *,
    previous_version: str,
    target_version: str,
) -> dict[str, Any]:
    _ = repo_root, previous_version, target_version
    migrated = deepcopy(registry)
    migrated["schema_version"] = 6
    for adr in migrated.get("adrs", []):
        status = adr.get("status")
        if status == "proposed":
            adr["status"] = "draft"
        adr.setdefault("supersedes", [])
        adr.setdefault("superseded_by", [])
        adr.setdefault("status_notes", [])
    for spec in migrated.get("specs", []):
        spec.setdefault("status", "draft")
        spec.setdefault("supersedes", [])
        spec.setdefault("superseded_by", [])
        spec.setdefault("status_notes", [])
    return migrated


def migrate_v6_to_v7(
    registry: dict[str, Any],
    repo_root: Path,
    *,
    previous_version: str,
    target_version: str,
) -> dict[str, Any]:
    _ = repo_root, previous_version, target_version
    migrated = deepcopy(registry)
    migrated["schema_version"] = 7
    repo = migrated.setdefault("repo", {})
    if not isinstance(repo, dict):
        migrated["repo"] = {"kind": "operator-repo"}
    else:
        repo.setdefault("kind", "operator-repo")

    migrated["document_id_reservations"] = default_document_id_reservations()
    for section in ("adrs", "specs"):
        for row in migrated.get(section, []):
            if row.get("origin") == "ssot-core":
                row["origin"] = "ssot-origin"
            if section == "specs" and row.get("kind") == "repo-local":
                row["kind"] = "local-policy"
    return migrated


def _manifest_id_map(kind: str) -> dict[int, str]:
    return {entry["number"]: entry["id"] for entry in load_document_manifest(kind)}


def _remove_legacy_ssot_origin_documents(
    registry: dict[str, Any],
    repo_root: Path,
    kind: str,
) -> dict[str, str]:
    section = "adrs" if kind == "adr" else "specs"
    manifest_id_by_number = _manifest_id_map(kind)
    retained: list[dict[str, Any]] = []
    remapped_ids: dict[str, str] = {}

    for row in registry.get(section, []):
        if row.get("origin") != "ssot-origin":
            retained.append(row)
            continue

        old_id = row.get("id")
        number = row.get("number")
        if isinstance(old_id, str) and isinstance(number, int) and number < 600:
            remapped_ids[old_id] = manifest_id_by_number.get(number + SSOT_ORIGIN_V8_OFFSET, old_id)

        path_value = row.get("path")
        if isinstance(path_value, str):
            target = repo_root / path_value
            if target.exists():
                target.unlink()

    registry[section] = retained
    return remapped_ids


def _remap_document_links(registry: dict[str, Any], remapped_ids: dict[str, str]) -> None:
    if not remapped_ids:
        return
    for section in ("adrs", "specs"):
        for row in registry.get(section, []):
            for field_name in ("supersedes", "superseded_by"):
                value = row.get(field_name)
                if isinstance(value, list):
                    row[field_name] = [remapped_ids.get(ref_id, ref_id) for ref_id in value]


def migrate_v7_to_v8(
    registry: dict[str, Any],
    repo_root: Path,
    *,
    previous_version: str,
    target_version: str,
) -> dict[str, Any]:
    _ = previous_version, target_version
    migrated = deepcopy(registry)
    migrated["schema_version"] = 8
    migrated["document_id_reservations"] = default_document_id_reservations()

    repo = migrated.get("repo")
    repo_kind = repo.get("kind") if isinstance(repo, dict) else "operator-repo"
    if repo_kind != "operator-repo":
        return migrated

    remapped_ids: dict[str, str] = {}
    remapped_ids.update(_remove_legacy_ssot_origin_documents(migrated, repo_root, "adr"))
    remapped_ids.update(_remove_legacy_ssot_origin_documents(migrated, repo_root, "spec"))
    _remap_document_links(migrated, remapped_ids)

    sync_documents_in_memory(migrated, repo_root, "adr")
    sync_documents_in_memory(migrated, repo_root, "spec")
    return migrated


def target_version_from_registry(registry: dict[str, Any]) -> str:
    tooling = registry.get("tooling")
    if isinstance(tooling, dict):
        value = tooling.get("ssot_registry_version")
        if isinstance(value, str) and value.strip():
            return value
    return __version__


def upgrade_registry(
    path: str | Path,
    *,
    target_version: str | None = None,
    sync_docs: bool = False,
    write_report: bool = False,
) -> dict[str, Any]:
    if target_version is not None and target_version != __version__:
        raise RegistryError(
            f"Installed ssot-registry version is {__version__}; install {target_version} before running upgrade"
        )

    target_version = __version__
    registry_path, repo_root, registry = load_registry(path)
    source_schema = registry.get("schema_version")
    source_tooling_version = registry.get("tooling", {}).get("ssot_registry_version", LEGACY_V3_VERSION)
    migrations: list[str] = []
    rename_summary: list[dict[str, str]] = []
    sync_summary: dict[str, dict[str, list[str]]] | None = None

    working = deepcopy(registry)

    if source_schema == 3:
        rename_summary = _rename_legacy_packaged_specs(working, repo_root)
        working = migrate_v3_to_v4(working, repo_root, previous_version=source_tooling_version, target_version=target_version)
        migrations.append("migrate_v3_to_v4")
        source_schema = 4
    if source_schema == 4:
        working = migrate_v4_to_v5(working, repo_root, previous_version=source_tooling_version, target_version=target_version)
        migrations.append("migrate_v4_to_v5")
        source_schema = 5
    if source_schema == 5:
        working = migrate_v5_to_v6(working, repo_root, previous_version=source_tooling_version, target_version=target_version)
        migrations.append("migrate_v5_to_v6")
        source_schema = 6
    if source_schema == 6:
        working = migrate_v6_to_v7(working, repo_root, previous_version=source_tooling_version, target_version=target_version)
        migrations.append("migrate_v6_to_v7")
        source_schema = 7
    if source_schema == 7:
        working = migrate_v7_to_v8(working, repo_root, previous_version=source_tooling_version, target_version=target_version)
        migrations.append("migrate_v7_to_v8")
    elif source_schema != SCHEMA_VERSION:
        raise RegistryError(f"Unsupported registry schema_version {source_schema}; expected 3, 4, 5, 6, 7 or {SCHEMA_VERSION}")

    if not migrations and not sync_docs:
        report = validate_registry_document(working, registry_path, repo_root)
        if not report["passed"]:
            raise ValidationError("; ".join(report["failures"]))
        result = {
            "passed": True,
            "registry_path": registry_path.as_posix(),
            "from_schema_version": source_schema,
            "to_schema_version": working.get("schema_version"),
            "from_version": source_tooling_version,
            "to_version": target_version,
            "migrations": migrations,
            "renamed_specs": rename_summary,
            "sync": None,
            "changed": False,
        }
        if write_report:
            report_path = repo_root / ".ssot" / "reports" / "upgrade.report.json"
            save_json(report_path, result)
            result["report_path"] = report_path.as_posix()
        return result

    tooling = working.setdefault("tooling", {})
    initialized_with = tooling.get("initialized_with_version") or source_tooling_version or target_version
    tooling["initialized_with_version"] = initialized_with
    tooling["last_upgraded_from_version"] = source_tooling_version
    tooling["ssot_registry_version"] = target_version

    if sync_docs:
        sync_summary = {
            "adr": sync_documents_in_memory(working, repo_root, "adr"),
            "spec": sync_documents_in_memory(working, repo_root, "spec"),
        }

    report = validate_registry_document(working, registry_path, repo_root)
    if not report["passed"]:
        raise ValidationError("; ".join(report["failures"]))

    save_registry(registry_path, working)
    result = {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "from_schema_version": source_schema,
        "to_schema_version": working.get("schema_version"),
        "from_version": source_tooling_version,
        "to_version": target_version,
        "migrations": migrations,
        "renamed_specs": rename_summary,
        "sync": sync_summary,
        "changed": True,
    }
    if write_report:
        report_path = repo_root / ".ssot" / "reports" / "upgrade.report.json"
        save_json(report_path, result)
        result["report_path"] = report_path.as_posix()
    return result
