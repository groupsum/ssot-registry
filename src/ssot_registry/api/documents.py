from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from ssot_registry.guards.document_lifecycle import (
    apply_status_transition,
    append_status_note,
    assert_mutable_document,
    validate_create_status,
)
from ssot_registry.guards.document_supersession import apply_supersession
from ssot_registry.model.document import (
    DOCUMENT_STATUSES,
    DOCUMENT_SLUG_PATTERN,
    SPEC_KINDS,
    build_document_path,
    default_document_id_reservations,
    load_document_manifest as load_packaged_document_manifest,
    normalize_document_id,
    read_packaged_document_bytes,
    read_packaged_document_text,
    reservation_kind_key,
    section_for_document_kind,
)
from ssot_registry.util.errors import ValidationError
from ssot_registry.util.fs import sha256_path
from ssot_registry.version import __version__

from .load import load_registry
from .save import save_registry
from .validate import validate_registry_document


def load_document_manifest(kind: str) -> list[dict[str, Any]]:
    return deepcopy(load_packaged_document_manifest(kind))


def _document_label(kind: str) -> str:
    return "ADR" if kind == "adr" else "spec"


def _row_lookup(registry: dict[str, Any], kind: str) -> dict[str, dict[str, Any]]:
    section = section_for_document_kind(kind)
    rows = registry.get(section, [])
    if not isinstance(rows, list):
        return {}
    return {row["id"]: row for row in rows if isinstance(row, dict) and isinstance(row.get("id"), str)}


def _sort_document_rows(registry: dict[str, Any], kind: str) -> None:
    section = section_for_document_kind(kind)
    registry[section] = sorted(
        registry.get(section, []),
        key=lambda row: (row.get("number", 0), row.get("id", "")),
    )


def _read_body(body_file: str | Path) -> str:
    return Path(body_file).read_text(encoding="utf-8").strip()


def _render_markdown(kind: str, number: int, title: str, body: str) -> str:
    if kind == "adr":
        heading = f"# ADR-{number:04d}: {title}"
    else:
        heading = f"# {title}"
    body = body.strip()
    if body:
        return f"{heading}\n\n{body}\n"
    return f"{heading}\n"


def _write_document(repo_root: Path, row: dict[str, Any], body: str, kind: str) -> str:
    target = repo_root / row["path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_render_markdown(kind, row["number"], row["title"], body), encoding="utf-8")
    return sha256_path(target)


def _build_repo_local_row(
    registry: dict[str, Any],
    kind: str,
    *,
    number: int,
    slug: str,
    title: str,
    content_sha256: str,
    status: str | None = None,
    note: str | None = None,
    spec_kind: str | None = None,
) -> dict[str, Any]:
    row = {
        "id": normalize_document_id(kind, number),
        "number": number,
        "slug": slug,
        "title": title,
        "path": build_document_path(registry["paths"], kind, number, slug),
        "origin": "repo-local",
        "managed": False,
        "immutable": False,
        "package_version": registry.get("tooling", {}).get("ssot_registry_version", __version__),
        "content_sha256": content_sha256,
    }
    row["status"] = status or "draft"
    row["supersedes"] = []
    row["superseded_by"] = []
    row["status_notes"] = []
    if note is not None:
        append_status_note(row, status=row["status"], note=note)
    if kind == "spec":
        row["kind"] = spec_kind or "repo-local"
    return row


def _manifest_row_to_registry_row(registry: dict[str, Any], kind: str, manifest_entry: dict[str, Any]) -> dict[str, Any]:
    row = {
        "id": manifest_entry["id"],
        "number": manifest_entry["number"],
        "slug": manifest_entry["slug"],
        "title": manifest_entry["title"],
        "path": manifest_entry["target_path"],
        "origin": manifest_entry["origin"],
        "managed": True,
        "immutable": bool(manifest_entry["immutable"]),
        "package_version": __version__,
        "content_sha256": manifest_entry["sha256"],
    }
    row["status"] = manifest_entry.get("status", "accepted")
    row["supersedes"] = manifest_entry.get("supersedes", [])
    row["superseded_by"] = manifest_entry.get("superseded_by", [])
    row["status_notes"] = manifest_entry.get("status_notes", [])
    if kind == "spec":
        row["kind"] = manifest_entry.get("kind", "normative")
    return row


def _existing_numbers(registry: dict[str, Any], kind: str) -> set[int]:
    return {
        row["number"]
        for row in registry.get(section_for_document_kind(kind), [])
        if isinstance(row, dict) and isinstance(row.get("number"), int)
    }


def _reservation_rows(registry: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    reservations = registry.get("document_id_reservations", default_document_id_reservations())
    rows = reservations.get(reservation_kind_key(kind), [])
    if not isinstance(rows, list):
        raise ValidationError(f"document_id_reservations.{reservation_kind_key(kind)} must be a list")
    return rows


def _reservation_for_number(registry: dict[str, Any], kind: str, number: int) -> dict[str, Any]:
    matches = [
        row
        for row in _reservation_rows(registry, kind)
        if isinstance(row.get("start"), int) and isinstance(row.get("end"), int) and row["start"] <= number <= row["end"]
    ]
    if len(matches) != 1:
        raise ValidationError(f"{_document_label(kind)} number {number} must belong to exactly one reservation")
    return matches[0]


def _ensure_assignable_number(registry: dict[str, Any], kind: str, number: int) -> None:
    reservation = _reservation_for_number(registry, kind, number)
    if not reservation.get("assignable_by_repo"):
        raise ValidationError(
            f"{_document_label(kind)} number {number} belongs to non-assignable reservation owned by {reservation.get('owner')}"
        )
    if number in _existing_numbers(registry, kind):
        raise ValidationError(f"{_document_label(kind)} number already exists: {number}")


def _allocate_number(registry: dict[str, Any], kind: str, reserve_range: str | None) -> int:
    used = _existing_numbers(registry, kind)
    candidates = []
    for row in _reservation_rows(registry, kind):
        if not row.get("assignable_by_repo"):
            continue
        if reserve_range is not None and row.get("owner") != reserve_range:
            continue
        if isinstance(row.get("start"), int) and isinstance(row.get("end"), int):
            candidates.append(row)
    candidates.sort(key=lambda row: (row["start"], row["end"], row.get("owner", "")))

    if reserve_range is not None and not candidates:
        raise ValidationError(f"Unknown assignable {kind} reservation: {reserve_range}")

    for reservation in candidates:
        for number in range(reservation["start"], reservation["end"] + 1):
            if number not in used:
                return number

    raise ValidationError(f"No available {_document_label(kind)} numbers remain in assignable reservations")


def _validate_and_save(registry_path: Path, repo_root: Path, registry: dict[str, Any], action: str) -> dict[str, Any]:
    report = validate_registry_document(registry, registry_path, repo_root)
    if not report["passed"]:
        detail = "; ".join(report["failures"])
        raise ValidationError(f"Registry validation failed after {action}: {detail}")
    save_registry(registry_path, registry)
    return report


def list_documents(path: str | Path, kind: str) -> dict[str, Any]:
    registry_path, _repo_root, registry = load_registry(path)
    section = section_for_document_kind(kind)
    documents = sorted((deepcopy(row) for row in registry.get(section, [])), key=lambda row: (row["number"], row["id"]))
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "section": section,
        "count": len(documents),
        "documents": documents,
    }


def get_document(path: str | Path, kind: str, document_id: str) -> dict[str, Any]:
    registry_path, _repo_root, registry = load_registry(path)
    try:
        document = deepcopy(_row_lookup(registry, kind)[document_id])
    except KeyError as exc:
        raise ValueError(f"Unknown {_document_label(kind)} id: {document_id}") from exc
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "section": section_for_document_kind(kind),
        "document": document,
    }


def create_document(
    path: str | Path,
    kind: str,
    *,
    title: str,
    slug: str,
    body_file: str | Path,
    number: int | None = None,
    origin: str = "repo-local",
    reserve_range: str | None = None,
    status: str | None = None,
    note: str | None = None,
    spec_kind: str | None = None,
) -> dict[str, Any]:
    if origin != "repo-local":
        raise ValidationError(f"Only repo-local {_document_label(kind)} creation is supported")
    if not isinstance(title, str) or not title.strip():
        raise ValidationError(f"{_document_label(kind)} title must be a non-empty string")
    if not isinstance(slug, str) or DOCUMENT_SLUG_PATTERN.match(slug) is None:
        raise ValidationError(f"{_document_label(kind)} slug must match ^[a-z0-9]+(?:-[a-z0-9]+)*$")
    if status is not None:
        validate_create_status(status)
    if kind == "spec" and spec_kind is not None and spec_kind not in SPEC_KINDS:
        raise ValidationError(f"Spec kind must be one of {sorted(SPEC_KINDS)}")

    registry_path, repo_root, registry = load_registry(path)
    if number is None:
        number = _allocate_number(registry, kind, reserve_range)
    else:
        _ensure_assignable_number(registry, kind, number)

    body = _read_body(body_file)
    provisional = _build_repo_local_row(
        registry,
        kind,
        number=number,
        slug=slug,
        title=title,
        content_sha256="0" * 64,
        status=status,
        note=note,
        spec_kind=spec_kind,
    )
    content_sha256 = _write_document(repo_root, provisional, body, kind)
    row = _build_repo_local_row(
        registry,
        kind,
        number=number,
        slug=slug,
        title=title,
        content_sha256=content_sha256,
        status=status,
        note=note,
        spec_kind=spec_kind,
    )

    section = section_for_document_kind(kind)
    registry[section].append(row)
    _sort_document_rows(registry, kind)
    _validate_and_save(registry_path, repo_root, registry, f"creating {kind} {row['id']}")
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "section": section,
        "document": deepcopy(row),
    }


def update_document(
    path: str | Path,
    kind: str,
    document_id: str,
    *,
    title: str | None = None,
    body_file: str | Path | None = None,
    status: str | None = None,
    note: str | None = None,
    spec_kind: str | None = None,
) -> dict[str, Any]:
    registry_path, repo_root, registry = load_registry(path)
    lookup = _row_lookup(registry, kind)
    try:
        row = lookup[document_id]
    except KeyError as exc:
        raise ValueError(f"Unknown {_document_label(kind)} id: {document_id}") from exc

    assert_mutable_document(row, label=_document_label(kind), document_id=document_id)
    if title is not None and not title.strip():
        raise ValidationError(f"{_document_label(kind)} title must be a non-empty string")
    if status is not None and status not in DOCUMENT_STATUSES:
        raise ValidationError(f"{_document_label(kind)} status must be one of {list(DOCUMENT_STATUSES)}")
    if kind == "spec" and spec_kind is not None and spec_kind not in SPEC_KINDS:
        raise ValidationError(f"Spec kind must be one of {sorted(SPEC_KINDS)}")

    if title is not None:
        row["title"] = title
    if status is not None:
        apply_status_transition(row, new_status=status, note=note)
    elif note is not None:
        append_status_note(row, status=row.get("status", "draft"), note=note)
    if kind == "spec" and spec_kind is not None:
        row["kind"] = spec_kind

    if body_file is None:
        body_text = (repo_root / row["path"]).read_text(encoding="utf-8").split("\n", 2)
        if len(body_text) == 1:
            body = ""
        elif len(body_text) == 2:
            body = body_text[1].strip()
        else:
            body = body_text[2].strip()
    else:
        body = _read_body(body_file)

    row["content_sha256"] = _write_document(repo_root, row, body, kind)
    row["package_version"] = registry.get("tooling", {}).get("ssot_registry_version", __version__)
    _sort_document_rows(registry, kind)
    _validate_and_save(registry_path, repo_root, registry, f"updating {kind} {document_id}")
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "section": section_for_document_kind(kind),
        "document": deepcopy(row),
    }


def delete_document(path: str | Path, kind: str, document_id: str) -> dict[str, Any]:
    registry_path, repo_root, registry = load_registry(path)
    section = section_for_document_kind(kind)
    lookup = _row_lookup(registry, kind)
    try:
        row = lookup[document_id]
    except KeyError as exc:
        raise ValueError(f"Unknown {_document_label(kind)} id: {document_id}") from exc

    reservation = _reservation_for_number(registry, kind, row["number"])
    if row.get("origin") == "ssot-core" or row.get("immutable") or not reservation.get("deletable"):
        raise ValidationError(f"{_document_label(kind)} {document_id} is immutable and cannot be deleted")

    target = repo_root / row["path"]
    if target.exists():
        target.unlink()

    registry[section] = [candidate for candidate in registry.get(section, []) if candidate.get("id") != document_id]
    _validate_and_save(registry_path, repo_root, registry, f"deleting {kind} {document_id}")
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "section": section,
        "deleted_id": document_id,
    }


def set_document_status(
    path: str | Path,
    kind: str,
    document_id: str,
    *,
    status: str,
    note: str | None = None,
) -> dict[str, Any]:
    return update_document(path, kind, document_id, status=status, note=note)


def supersede_documents(
    path: str | Path,
    kind: str,
    source_id: str,
    *,
    supersedes: list[str],
    note: str | None = None,
) -> dict[str, Any]:
    registry_path, repo_root, registry = load_registry(path)
    section = section_for_document_kind(kind)
    rows = _row_lookup(registry, kind)
    apply_supersession(rows, source_id=source_id, target_ids=supersedes, label=_document_label(kind), note=note)
    _sort_document_rows(registry, kind)
    _validate_and_save(registry_path, repo_root, registry, f"superseding {kind} {source_id}")
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "section": section,
        "document": deepcopy(rows[source_id]),
    }


def _sync_manifest_document(
    registry: dict[str, Any],
    repo_root: Path,
    kind: str,
    manifest_entry: dict[str, Any],
    lookup: dict[str, dict[str, Any]],
) -> tuple[str, str]:
    expected_row = _manifest_row_to_registry_row(registry, kind, manifest_entry)
    document_id = expected_row["id"]
    current = lookup.get(document_id)
    if current is None:
        for row in registry.get(section_for_document_kind(kind), []):
            if row.get("number") == expected_row["number"] and row.get("id") != document_id:
                raise ValidationError(
                    f"Cannot sync {document_id}; number {expected_row['number']} is already used by {row.get('id')}"
                )
        payload = read_packaged_document_bytes(kind, manifest_entry["filename"])
        target = repo_root / expected_row["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        registry[section_for_document_kind(kind)].append(expected_row)
        lookup[document_id] = expected_row
        return "created", document_id

    for field_name in ("number", "slug", "path", "origin", "managed", "immutable"):
        if current.get(field_name) != expected_row.get(field_name):
            raise ValidationError(
                f"Cannot sync {document_id}; field {field_name} was locally modified from {expected_row.get(field_name)} to {current.get(field_name)}"
            )

    payload = read_packaged_document_bytes(kind, manifest_entry["filename"])
    target = repo_root / expected_row["path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    actual_hash = sha256_path(target) if target.exists() else None
    needs_write = (
        actual_hash != expected_row["content_sha256"]
        or current.get("content_sha256") != expected_row["content_sha256"]
        or current.get("package_version") != expected_row["package_version"]
        or current.get("title") != expected_row["title"]
        or current.get("status") != expected_row["status"]
        or current.get("supersedes") != expected_row["supersedes"]
        or current.get("superseded_by") != expected_row["superseded_by"]
        or current.get("status_notes") != expected_row["status_notes"]
        or (kind == "spec" and current.get("kind") != expected_row["kind"])
    )
    if needs_write:
        target.write_bytes(payload)
        current.clear()
        current.update(expected_row)
        return "updated", document_id

    current.update(expected_row)
    return "unchanged", document_id


def sync_documents_in_memory(registry: dict[str, Any], repo_root: Path, kind: str) -> dict[str, list[str]]:
    section = section_for_document_kind(kind)
    lookup = _row_lookup(registry, kind)
    summary: dict[str, list[str]] = {"created": [], "updated": [], "unchanged": []}

    for manifest_entry in load_packaged_document_manifest(kind):
        if manifest_entry.get("minimum_schema_version", 0) > registry.get("schema_version", 0):
            continue
        outcome, document_id = _sync_manifest_document(registry, repo_root, kind, manifest_entry, lookup)
        summary[outcome].append(document_id)

    _sort_document_rows(registry, kind)
    if section not in registry:
        registry[section] = []
    return summary


def sync_documents(path: str | Path, kind: str) -> dict[str, Any]:
    registry_path, repo_root, registry = load_registry(path)
    section = section_for_document_kind(kind)
    summary = sync_documents_in_memory(registry, repo_root, kind)
    _validate_and_save(registry_path, repo_root, registry, f"syncing {kind} documents")
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "section": section,
        **summary,
    }


def sync_all_documents(path: str | Path) -> dict[str, Any]:
    adr_result = sync_documents(path, "adr")
    spec_result = sync_documents(path, "spec")
    return {
        "passed": True,
        "registry_path": adr_result["registry_path"],
        "adr": {key: adr_result[key] for key in ("created", "updated", "unchanged")},
        "spec": {key: spec_result[key] for key in ("created", "updated", "unchanged")},
    }


def create_document_reservation(path: str | Path, kind: str, *, name: str, start: int, end: int) -> dict[str, Any]:
    registry_path, repo_root, registry = load_registry(path)
    row = {
        "owner": name,
        "start": start,
        "end": end,
        "immutable": False,
        "deletable": True,
        "assignable_by_repo": True,
    }
    registry["document_id_reservations"][reservation_kind_key(kind)].append(row)
    _validate_and_save(registry_path, repo_root, registry, f"creating {kind} reservation {name}")
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "kind": kind,
        "reservation": deepcopy(row),
    }


def list_document_reservations(path: str | Path, kind: str) -> dict[str, Any]:
    registry_path, _repo_root, registry = load_registry(path)
    reservations = sorted(
        (deepcopy(row) for row in _reservation_rows(registry, kind)),
        key=lambda row: (row["start"], row["end"], row["owner"]),
    )
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "kind": kind,
        "count": len(reservations),
        "reservations": reservations,
    }
