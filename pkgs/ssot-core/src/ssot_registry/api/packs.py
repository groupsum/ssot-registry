from __future__ import annotations

import hashlib
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from ssot_pack_contracts import (
    InvalidPackManifestError,
    load_document_manifest,
    load_pack_manifest,
    load_pack_metadata,
    normalize_document_kind,
    read_packaged_document_bytes,
)

from ssot_registry.model.document import build_document_path
from ssot_registry.model.document import reservation_kind_key
from ssot_registry.model.document import section_for_document_kind
from ssot_registry.model.schema_version import schema_version_meets_minimum
from ssot_registry.util.document_io import dump_document_text, load_document_text
from ssot_registry.util.errors import ValidationError
from ssot_registry.util.fs import sha256_normalized_text_path

from .documents import _validate_and_save
from .load import load_registry


def inspect_pack(package: str) -> dict[str, Any]:
    metadata = load_pack_metadata(package)
    manifest = load_pack_manifest(package)
    return {
        "passed": True,
        "package": package,
        "metadata": metadata,
        "document_counts": {kind: len(rows) for kind, rows in manifest["documents"].items()},
        "documents": manifest["documents"],
    }


def _declared_entries(package: str, kind: str | None = None) -> list[dict[str, Any]]:
    if kind is not None:
        return load_document_manifest(package, normalize_document_kind(kind))
    entries: list[dict[str, Any]] = []
    manifest = load_pack_manifest(package)
    for document_kind, rows in manifest["documents"].items():
        for row in rows:
            copied = dict(row)
            copied["_document_kind"] = document_kind
            entries.append(copied)
    return entries


def _metadata_version(metadata: dict[str, Any]) -> str:
    return str(metadata.get("version") or metadata.get("origin", {}).get("version") or "")


def _pack_id(metadata: dict[str, Any]) -> str:
    origin = metadata.get("origin")
    if isinstance(origin, dict) and isinstance(origin.get("id"), str) and origin["id"].strip():
        return origin["id"]
    package_name = str(metadata.get("ssot_package_name") or "unknown-pack").strip()
    return f"pack:{package_name}"


def _pack_package_name(metadata: dict[str, Any], package: str) -> str:
    origin = metadata.get("origin")
    if isinstance(origin, dict) and isinstance(origin.get("package_name"), str) and origin["package_name"].strip():
        return origin["package_name"]
    if isinstance(metadata.get("ssot_package_name"), str) and metadata["ssot_package_name"].strip():
        return metadata["ssot_package_name"]
    return package


def _id_part(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9._-]+", "-", value.lower()).strip("-._")
    return normalized or "document"


def _slug_part(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "document"


def _shorten_part(value: str, *, max_length: int) -> str:
    if len(value) <= max_length:
        return value
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:10]
    return f"{value[: max_length - 11].rstrip('-._')}-{digest}"


def _source_document_suffix(source_id: str) -> str:
    if ":" in source_id:
        source_id = source_id.split(":", 1)[1]
    return _id_part(source_id)


def _materialized_document_id(kind: str, pack_id: str, source_id: str) -> str:
    prefix = "adr:" if kind == "adr" else "spc:"
    pack_suffix = _id_part(pack_id.split(":", 1)[1] if ":" in pack_id else pack_id)
    source_suffix = _source_document_suffix(source_id)
    suffix = _shorten_part(f"pack.{pack_suffix}.{source_suffix}", max_length=124)
    return f"{prefix}{suffix}"


def _materialized_number(kind: str, pack_id: str, source_id: str) -> int:
    digest = hashlib.sha1(f"{kind}:{pack_id}:{source_id}".encode("utf-8")).hexdigest()
    return 100000 + (int(digest[:10], 16) % 900000000)


def _materialized_slug(pack_id: str, source_id: str) -> str:
    pack_suffix = _slug_part(pack_id.split(":", 1)[1] if ":" in pack_id else pack_id)
    source_suffix = _slug_part(source_id.split(":", 1)[1] if ":" in source_id else source_id)
    return _shorten_part(f"pack-{pack_suffix}-{source_suffix}", max_length=96)


def _source_ref_key(row: dict[str, Any]) -> tuple[str, str, str] | None:
    pack_id = row.get("source_pack_id")
    document_kind = row.get("source_document_kind")
    document_id = row.get("source_document_id")
    if isinstance(pack_id, str) and isinstance(document_kind, str) and isinstance(document_id, str):
        if pack_id and document_kind and document_id:
            return pack_id, document_kind, document_id
    return None


def _materialize_entry(
    entry: dict[str, Any],
    metadata: dict[str, Any],
    package: str,
    registry: dict[str, Any],
) -> dict[str, Any]:
    document_kind = str(entry.get("_document_kind") or ("adr" if str(entry["id"]).startswith("adr:") else "spec"))
    if entry.get("origin") != "extension-pack":
        materialized = dict(entry)
        materialized["_document_kind"] = document_kind
        return materialized

    pack_id = _pack_id(metadata)
    source_id = str(entry["id"])
    materialized = dict(entry)
    materialized["_document_kind"] = document_kind
    materialized["source_pack_id"] = pack_id
    materialized["source_package_name"] = _pack_package_name(metadata, package)
    materialized["source_document_kind"] = document_kind
    materialized["source_document_id"] = source_id
    materialized["id"] = _materialized_document_id(document_kind, pack_id, source_id)
    materialized["number"] = _materialized_number(document_kind, pack_id, source_id)
    materialized["slug"] = _materialized_slug(pack_id, source_id)
    materialized["target_path"] = build_document_path(registry.get("paths", {}), document_kind, materialized["number"], materialized["slug"])
    return materialized


def _materialized_entries(
    package: str,
    metadata: dict[str, Any],
    registry: dict[str, Any],
    kind: str | None = None,
) -> list[dict[str, Any]]:
    return [_materialize_entry(entry, metadata, package, registry) for entry in _declared_entries(package, kind)]


def _rewrite_document_payload(payload_bytes: bytes, document_kind: str, row: dict[str, Any]) -> bytes:
    text = payload_bytes.decode("utf-8-sig")
    payload = load_document_text(text, source=f"packaged:{row.get('source_document_id', row['id'])}")
    payload["id"] = row["id"]
    payload["number"] = row["number"]
    payload["slug"] = row["slug"]
    payload["title"] = row["title"]
    payload["status"] = row["status"]
    payload["origin"] = row["origin"]
    payload["supersedes"] = list(row.get("supersedes", []))
    payload["superseded_by"] = list(row.get("superseded_by", []))
    payload["status_notes"] = list(row.get("status_notes", []))
    if document_kind == "spec":
        payload["spec_kind"] = row.get("kind", "normative")
        payload["adr_ids"] = list(row.get("adr_ids", []))
    return dump_document_text(payload, row["path"]).encode("utf-8")


def _check_pin(metadata: dict[str, Any], pin: str | None) -> None:
    if pin is None:
        return
    version = _metadata_version(metadata)
    if version != pin:
        raise ValidationError(f"Pack version {version!r} does not match pinned version {pin!r}")


def preflight_pack(
    path: str | Path,
    package: str,
    *,
    kind: str | None = None,
    trusted_only: bool = False,
    pin: str | None = None,
    include_manifest: bool = False,
    include_resolved: bool = False,
) -> dict[str, Any]:
    registry_path, repo_root, registry = load_registry(path)
    metadata = load_pack_metadata(package)
    _check_pin(metadata, pin)
    if trusted_only and not bool(metadata.get("trust", {}).get("trusted_by_default")):
        raise ValidationError(f"Pack {package} is not trusted by default")

    entries = _declared_entries(package, kind)
    resolved_entries = _materialized_entries(package, metadata, registry, kind)
    failures: list[str] = []
    seen_ids: dict[str, str] = {}
    seen_numbers: dict[tuple[str, int], str] = {}
    seen_targets: dict[str, str] = {}
    for entry in entries:
        document_kind = str(entry.get("_document_kind") or ("adr" if str(entry["id"]).startswith("adr:") else "spec"))
        entry_id = str(entry["id"])
        if entry_id in seen_ids:
            failures.append(f"duplicate manifest document id {entry_id}")
        seen_ids[entry_id] = document_kind
        number_key = (document_kind, int(entry["number"]))
        if number_key in seen_numbers:
            failures.append(f"duplicate {document_kind} manifest number {entry['number']}")
        seen_numbers[number_key] = entry_id
        target_path = str(entry["target_path"])
        if target_path in seen_targets:
            failures.append(f"duplicate manifest target_path {target_path}")
        seen_targets[target_path] = entry_id
        if not schema_version_meets_minimum(registry.get("schema_version", 0), entry.get("minimum_schema_version", 0)):
            failures.append(f"{entry_id} requires schema {entry.get('minimum_schema_version')}")
        try:
            read_packaged_document_bytes(package, document_kind, str(entry["filename"]))
        except InvalidPackManifestError as exc:
            failures.append(str(exc))

    for document_kind in ("adr", "spec"):
        section = section_for_document_kind(document_kind)
        existing_by_id = {row.get("id"): row for row in registry.get(section, []) if isinstance(row, dict)}
        existing_by_number = {row.get("number"): row for row in registry.get(section, []) if isinstance(row, dict)}
        existing_by_path = {row.get("path"): row for row in registry.get(section, []) if isinstance(row, dict)}
        existing_by_source = {
            key: row
            for row in registry.get(section, [])
            if isinstance(row, dict)
            for key in [_source_ref_key(row)]
            if key is not None
        }
        for entry in [row for row in resolved_entries if row.get("_document_kind", document_kind) == document_kind]:
            current = existing_by_id.get(entry["id"])
            if current is not None:
                for field_name, expected in (("number", entry["number"]), ("path", entry["target_path"]), ("origin", entry["origin"])):
                    if current.get(field_name) != expected:
                        failures.append(f"{entry['id']} conflicts with existing {field_name}: {current.get(field_name)}")
            number_owner = existing_by_number.get(entry["number"])
            if number_owner is not None and number_owner.get("id") != entry["id"]:
                failures.append(f"{entry['id']} number conflicts with {number_owner.get('id')}")
            path_owner = existing_by_path.get(entry["target_path"])
            if path_owner is not None and path_owner.get("id") != entry["id"]:
                failures.append(f"{entry['id']} target_path conflicts with {path_owner.get('id')}")
            source_owner = existing_by_source.get(_source_ref_key(entry))
            if source_owner is not None and source_owner.get("id") != entry["id"]:
                failures.append(f"{entry['id']} source document conflicts with {source_owner.get('id')}")

    result: dict[str, Any] = {
        "passed": not failures,
        "registry_path": registry_path.as_posix(),
        "package": package,
        "metadata": metadata,
        "checked": len(entries),
        "failures": failures,
    }
    if pin is not None:
        result["pin"] = pin
    if include_manifest:
        result["manifest"] = load_pack_manifest(package)
    if include_resolved:
        result["resolved"] = resolved_entries
    return result


def _row_from_entry(entry: dict[str, Any], *, package_version: str) -> dict[str, Any]:
    row = {
        "id": entry["id"],
        "number": entry["number"],
        "slug": entry["slug"],
        "title": entry["title"],
        "path": entry["target_path"],
        "origin": entry["origin"],
        "managed": True,
        "immutable": bool(entry["immutable"]),
        "package_version": package_version,
        "content_sha256": entry["sha256"],
        "status": entry.get("status", "draft"),
        "supersedes": list(entry.get("supersedes", [])),
        "superseded_by": list(entry.get("superseded_by", [])),
        "status_notes": list(entry.get("status_notes", [])),
    }
    if str(entry["id"]).startswith("spc:"):
        row["kind"] = entry.get("kind", "normative")
        row["adr_ids"] = list(entry.get("adr_ids", []))
    for field_name in ("source_pack_id", "source_package_name", "source_document_kind", "source_document_id"):
        value = entry.get(field_name)
        if isinstance(value, str) and value:
            row[field_name] = value
    return row


def _ensure_extension_reservation(registry: dict[str, Any], kind: str, entry: dict[str, Any]) -> None:
    if entry.get("origin") != "extension-pack":
        return
    reservations = registry.setdefault("document_id_reservations", {})
    rows = reservations.setdefault(reservation_kind_key(kind), [])
    owner = str(entry["reservation_owner"])
    number = int(entry["number"])
    for row in rows:
        if row.get("owner") == owner and isinstance(row.get("start"), int) and isinstance(row.get("end"), int):
            if row["start"] <= number <= row["end"]:
                return
    rows.append(
        {
            "owner": owner,
            "start": number,
            "end": number,
            "immutable": True,
            "deletable": False,
            "assignable_by_repo": False,
        }
    )


def sync_pack(
    path: str | Path,
    package: str,
    *,
    kind: str | None = None,
    dry_run: bool = False,
    trusted_only: bool = False,
    pin: str | None = None,
    preflight_only: bool = False,
    no_sync: bool = False,
    prune_stale: bool = False,
    include_manifest: bool = False,
    include_resolved: bool = False,
    include_reservations: bool = False,
    trust: bool = False,
    yes: bool = False,
) -> dict[str, Any]:
    preflight = preflight_pack(
        path,
        package,
        kind=kind,
        trusted_only=trusted_only,
        pin=pin,
        include_manifest=include_manifest,
        include_resolved=include_resolved,
    )
    if not preflight["passed"]:
        return {**preflight, "dry_run": dry_run, "created": [], "updated": [], "unchanged": []}
    if preflight_only or no_sync:
        return {
            **preflight,
            "dry_run": True,
            "preflight_only": preflight_only,
            "no_sync": no_sync,
            "created": [],
            "updated": [],
            "unchanged": [],
            "stale": [],
            "pruned": [],
        }

    registry_path, repo_root, registry = load_registry(path)
    metadata = load_pack_metadata(package)
    _check_pin(metadata, pin)
    package_version = str(metadata["version"])
    entries = _materialized_entries(package, metadata, registry, kind)
    source_adr_ids: dict[tuple[str, str], str] = {}
    for row in registry.get("adrs", []):
        if not isinstance(row, dict):
            continue
        source_key = _source_ref_key(row)
        if source_key is not None and source_key[1] == "adr":
            source_adr_ids[(source_key[0], source_key[2])] = str(row["id"])
    for entry in entries:
        if entry.get("_document_kind") == "adr":
            source_key = _source_ref_key(entry)
            if source_key is not None:
                source_adr_ids[(source_key[0], source_key[2])] = str(entry["id"])
    for entry in entries:
        if entry.get("_document_kind") != "spec":
            continue
        source_key = _source_ref_key(entry)
        if source_key is None:
            continue
        entry["adr_ids"] = [source_adr_ids.get((source_key[0], str(adr_id)), str(adr_id)) for adr_id in entry.get("adr_ids", [])]
    created: list[str] = []
    updated: list[str] = []
    unchanged: list[str] = []
    touched_ids: set[str] = set()
    reservation_changes: list[dict[str, Any]] = []

    for entry in entries:
        document_kind = str(entry.get("_document_kind") or ("adr" if str(entry["id"]).startswith("adr:") else "spec"))
        section = section_for_document_kind(document_kind)
        row = _row_from_entry(entry, package_version=package_version)
        before_reservations = deepcopy(registry.get("document_id_reservations", {}).get(reservation_kind_key(document_kind), []))
        _ensure_extension_reservation(registry, document_kind, entry)
        after_reservations = registry.get("document_id_reservations", {}).get(reservation_kind_key(document_kind), [])
        if before_reservations != after_reservations:
            reservation_changes.append({"kind": document_kind, "owner": entry["reservation_owner"], "number": entry["number"]})
        touched_ids.add(str(entry["id"]))
        packaged_bytes = read_packaged_document_bytes(package, document_kind, str(entry["filename"]))
        if row.get("origin") == "extension-pack" and row.get("source_document_id"):
            packaged_bytes = _rewrite_document_payload(packaged_bytes, document_kind, row)
            row["content_sha256"] = hashlib.sha256(packaged_bytes).hexdigest()
        if not dry_run:
            target = repo_root / row["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(packaged_bytes)
            row["content_sha256"] = sha256_normalized_text_path(target)
        rows = registry.setdefault(section, [])
        current = next((candidate for candidate in rows if candidate.get("id") == entry["id"]), None)
        if current is None:
            created.append(entry["id"])
            if not dry_run:
                rows.append(row)
        elif current == row:
            unchanged.append(entry["id"])
        else:
            updated.append(entry["id"])
            if not dry_run:
                current.clear()
                current.update(row)
    stale: list[str] = []
    pruned: list[str] = []
    reservation_owner = str(metadata.get("trust", {}).get("reservation_owner", ""))
    if reservation_owner:
        for document_kind in ("adr", "spec"):
            section = section_for_document_kind(document_kind)
            rows = registry.setdefault(section, [])
            stale_rows = [
                row
                for row in rows
                if row.get("origin") == "extension-pack"
                and row.get("id") not in touched_ids
                and any(
                    reservation.get("owner") == reservation_owner
                    and isinstance(reservation.get("start"), int)
                    and isinstance(reservation.get("end"), int)
                    and reservation["start"] <= int(row.get("number", -1)) <= reservation["end"]
                    for reservation in registry.get("document_id_reservations", {}).get(reservation_kind_key(document_kind), [])
                )
            ]
            stale.extend(str(row["id"]) for row in stale_rows)
            if prune_stale and not dry_run:
                for row in stale_rows:
                    target = repo_root / str(row["path"])
                    if target.exists():
                        target.unlink()
                    pruned.append(str(row["id"]))
                registry[section] = [row for row in rows if row not in stale_rows]
    if not dry_run:
        for document_kind in ("adr", "spec"):
            section = section_for_document_kind(document_kind)
            registry[section] = sorted(registry.get(section, []), key=lambda row: (row.get("number", 0), row.get("id", "")))
        _validate_and_save(registry_path, repo_root, registry, f"syncing pack {package}")

    result: dict[str, Any] = {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "package": package,
        "dry_run": dry_run,
        "trusted_operator_approved": trust,
        "yes": yes,
        "created": created,
        "updated": updated,
        "unchanged": unchanged,
        "stale": stale,
        "pruned": pruned,
    }
    if pin is not None:
        result["pin"] = pin
    if include_manifest:
        result["manifest"] = load_pack_manifest(package)
    if include_resolved:
        result["resolved"] = entries
    if include_reservations:
        result["reservations"] = reservation_changes
    return result
