from __future__ import annotations

from pathlib import Path
from typing import Any

from ssot_registry.model.document import (
    DOCUMENT_STATUSES,
    DOCUMENT_ORIGINS,
    SPEC_KINDS,
    build_document_path,
    load_document_manifest,
    normalize_document_id,
    reservation_kind_key,
)
from ssot_registry.util.fs import sha256_path
from ssot_registry.version import __version__


def _reservation_matches(number: int, reservations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in reservations if isinstance(row.get("start"), int) and isinstance(row.get("end"), int) and row["start"] <= number <= row["end"]]


def _validate_status_notes(prefix: str, row: dict[str, Any], failures: list[str]) -> None:
    notes = row.get("status_notes", [])
    if not isinstance(notes, list):
        failures.append(f"{prefix}.status_notes must be a list")
        return
    for idx, note in enumerate(notes):
        if not isinstance(note, dict):
            failures.append(f"{prefix}.status_notes[{idx}] must be an object")
            continue
        status = note.get("status")
        if status not in DOCUMENT_STATUSES:
            failures.append(f"{prefix}.status_notes[{idx}].status must be one of {list(DOCUMENT_STATUSES)}")
        note_text = note.get("note")
        if not isinstance(note_text, str) or not note_text.strip():
            failures.append(f"{prefix}.status_notes[{idx}].note must be a non-empty string")
        at = note.get("at")
        if not isinstance(at, str) or not at.strip():
            failures.append(f"{prefix}.status_notes[{idx}].at must be a non-empty string")
        actor = note.get("actor")
        if actor is not None and not isinstance(actor, str):
            failures.append(f"{prefix}.status_notes[{idx}].actor must be a string when provided")
        reason = note.get("reason")
        if reason is not None and not isinstance(reason, str):
            failures.append(f"{prefix}.status_notes[{idx}].reason must be a string when provided")


def validate_document_rows(
    registry: dict[str, Any],
    index: dict[str, dict[str, dict[str, Any]]],
    repo_root: Path,
    failures: list[str],
) -> None:
    reservations = registry.get("document_id_reservations", {})
    paths = registry.get("paths", {})
    repo = registry.get("repo", {})
    repo_kind = repo.get("kind") if isinstance(repo, dict) else None
    if repo_kind not in {"ssot-upstream", "operator-repo"}:
        repo_kind = "operator-repo"

    manifest_lookup = {
        "adrs": {entry["id"]: entry for entry in load_document_manifest("adr")},
        "specs": {entry["id"]: entry for entry in load_document_manifest("spec")},
    }
    kinds = {
        "adrs": "adr",
        "specs": "spec",
    }

    for section, kind in kinds.items():
        rows = index.get(section, {})
        seen_numbers: dict[int, str] = {}
        seen_slugs: dict[str, str] = {}
        seen_paths: dict[str, str] = {}
        reservation_rows = reservations.get(reservation_kind_key(kind), [])
        if not isinstance(reservation_rows, list):
            failures.append(f"document_id_reservations.{reservation_kind_key(kind)} must be a list")
            reservation_rows = []

        for entity_id, row in rows.items():
            expected_id = normalize_document_id(kind, row.get("number")) if isinstance(row.get("number"), int) else None
            prefix = f"{section}.{entity_id}"
            for field_name in (
                "number",
                "slug",
                "title",
                "path",
                "origin",
                "managed",
                "immutable",
                "package_version",
                "content_sha256",
            ):
                if field_name not in row:
                    failures.append(f"{prefix} is missing required field: {field_name}")

            number = row.get("number")
            slug = row.get("slug")
            title = row.get("title")
            relative_path = row.get("path")
            origin = row.get("origin")
            managed = row.get("managed")
            immutable = row.get("immutable")
            package_version = row.get("package_version")
            content_sha256 = row.get("content_sha256")

            if not isinstance(number, int) or number < 1:
                failures.append(f"{prefix}.number must be an integer >= 1")
                continue
            if expected_id is not None and entity_id != expected_id:
                failures.append(f"{prefix}.id must match its number: expected {expected_id}")
            if not isinstance(slug, str) or not slug:
                failures.append(f"{prefix}.slug must be a non-empty string")
            if isinstance(slug, str):
                if slug in seen_slugs:
                    failures.append(f"Duplicate {section} slug: {slug} in {prefix} and {section}.{seen_slugs[slug]}")
                seen_slugs[slug] = entity_id
            if number in seen_numbers:
                failures.append(f"Duplicate {section} number: {number} in {prefix} and {section}.{seen_numbers[number]}")
            seen_numbers[number] = entity_id
            if not isinstance(title, str) or not title.strip():
                failures.append(f"{prefix}.title must be a non-empty string")
            if not isinstance(relative_path, str) or not relative_path.strip():
                failures.append(f"{prefix}.path must be a non-empty string")
            if isinstance(relative_path, str):
                if relative_path in seen_paths:
                    failures.append(f"Duplicate {section} path: {relative_path} in {prefix} and {section}.{seen_paths[relative_path]}")
                seen_paths[relative_path] = entity_id
                expected_path = build_document_path(paths, kind, number, slug) if isinstance(paths, dict) and isinstance(slug, str) else None
                if expected_path is not None and relative_path != expected_path:
                    failures.append(f"{prefix}.path must match number and slug: expected {expected_path}")
                full_path = repo_root / relative_path
                if not full_path.exists():
                    failures.append(f"{prefix}.path does not exist: {relative_path}")
                else:
                    actual_sha256 = sha256_path(full_path)
                    if not isinstance(content_sha256, str) or len(content_sha256) != 64:
                        failures.append(f"{prefix}.content_sha256 must be a 64-character sha256 hex digest")
                    elif actual_sha256 != content_sha256:
                        failures.append(f"{prefix} content hash does not match file content: {relative_path}")
            if origin not in DOCUMENT_ORIGINS:
                failures.append(f"{prefix}.origin must be one of {sorted(DOCUMENT_ORIGINS)}")
            if not isinstance(managed, bool):
                failures.append(f"{prefix}.managed must be a boolean")
            if not isinstance(immutable, bool):
                failures.append(f"{prefix}.immutable must be a boolean")
            if not isinstance(package_version, str) or not package_version.strip():
                failures.append(f"{prefix}.package_version must be a non-empty string")

            matching_reservations = _reservation_matches(number, reservation_rows)
            if len(matching_reservations) != 1:
                failures.append(f"{prefix}.number must belong to exactly one {kind} reservation")
                reservation = None
            else:
                reservation = matching_reservations[0]

            if reservation is not None and reservation.get("immutable") and origin == "repo-local":
                failures.append(f"{prefix} uses immutable {kind} reservation owned by {reservation.get('owner')} but origin is {origin}")
            if reservation is not None and origin in {"ssot-origin", "ssot-core"} and reservation.get("owner") != origin:
                failures.append(
                    f"{prefix}.number belongs to reservation owner {reservation.get('owner')} but origin is {origin}"
                )
            if repo_kind == "operator-repo":
                if origin == "ssot-core":
                    failures.append(f"{prefix}.origin must not be ssot-core in operator-repo")
                if origin == "ssot-origin":
                    if managed is not True:
                        failures.append(f"{prefix}.managed must be true for ssot-origin documents in operator-repo")
                    if immutable is not True:
                        failures.append(f"{prefix}.immutable must be true for ssot-origin documents in operator-repo")
                if origin == "repo-local":
                    if managed is not False:
                        failures.append(f"{prefix}.managed must be false for repo-local documents")
                    if immutable is not False:
                        failures.append(f"{prefix}.immutable must be false for repo-local documents")
            elif repo_kind == "ssot-upstream":
                if origin == "repo-local":
                    failures.append(f"{prefix}.origin must not be repo-local in ssot-upstream")
                if managed is not False:
                    failures.append(f"{prefix}.managed must be false in ssot-upstream")
                if immutable is not False:
                    failures.append(f"{prefix}.immutable must be false in ssot-upstream")

            if section == "adrs":
                pass
            if section == "specs":
                kind_value = row.get("kind")
                if kind_value not in SPEC_KINDS:
                    failures.append(f"{prefix}.kind must be one of {sorted(SPEC_KINDS)}")
            status = row.get("status")
            supersedes = row.get("supersedes")
            superseded_by = row.get("superseded_by")
            if status not in DOCUMENT_STATUSES:
                failures.append(f"{prefix}.status must be one of {list(DOCUMENT_STATUSES)}")
            if not isinstance(supersedes, list) or not all(isinstance(value, str) for value in supersedes):
                failures.append(f"{prefix}.supersedes must be a list of strings")
            if not isinstance(superseded_by, list) or not all(isinstance(value, str) for value in superseded_by):
                failures.append(f"{prefix}.superseded_by must be a list of strings")
            _validate_status_notes(prefix, row, failures)
            for field_name in ("supersedes", "superseded_by"):
                value = row.get(field_name, [])
                if isinstance(value, list):
                    for ref_id in value:
                        if ref_id not in rows:
                            failures.append(f"{prefix}.{field_name} references missing {kind} {ref_id}")
            if isinstance(supersedes, list) and isinstance(superseded_by, list):
                overlap = set(supersedes).intersection(superseded_by)
                if overlap:
                    failures.append(f"{prefix} has ids present in both supersedes and superseded_by: {sorted(overlap)}")
            if status == "superseded" and isinstance(superseded_by, list) and not superseded_by:
                failures.append(f"{prefix}.status is superseded but superseded_by is empty")
            if status != "superseded" and isinstance(superseded_by, list) and superseded_by:
                failures.append(f"{prefix}.superseded_by must be empty unless status is superseded")

            if repo_kind == "operator-repo" and origin == "ssot-origin":
                manifest_entry = manifest_lookup[section].get(entity_id)
                if manifest_entry is None:
                    failures.append(f"{prefix} is ssot-origin managed but not present in the packaged manifest")
                    continue
                if manifest_entry.get("origin") != "ssot-origin":
                    failures.append(f"packaged {kind} manifest entry {entity_id} must use origin ssot-origin")
                for field_name in ("number", "slug", "title"):
                    if row.get(field_name) != manifest_entry.get(field_name):
                        failures.append(f"{prefix}.{field_name} must match the packaged manifest")
                if row.get("path") != manifest_entry.get("target_path"):
                    failures.append(f"{prefix}.path must match packaged target path {manifest_entry.get('target_path')}")
                if package_version == __version__ and row.get("content_sha256") != manifest_entry.get("sha256"):
                    failures.append(f"{prefix} is SSOT-managed and immutable, but content hash differs from packaged source")
