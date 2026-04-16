from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ssot_registry.model.document import CREATE_ALLOWED_STATUSES, DOCUMENT_STATUSES, TRANSITION_RULES
from ssot_registry.util.errors import ValidationError


def validate_create_status(status: str) -> None:
    if status not in DOCUMENT_STATUSES:
        raise ValidationError(f"Document status must be one of {list(DOCUMENT_STATUSES)}")
    if status not in CREATE_ALLOWED_STATUSES:
        raise ValidationError(f"Document creation status must be one of {list(CREATE_ALLOWED_STATUSES)}")


def validate_transition(old_status: str, new_status: str) -> None:
    if new_status not in DOCUMENT_STATUSES:
        raise ValidationError(f"Document status must be one of {list(DOCUMENT_STATUSES)}")
    if old_status == new_status:
        return
    allowed = TRANSITION_RULES.get(old_status, set())
    if new_status not in allowed:
        raise ValidationError(f"Illegal lifecycle transition from {old_status} to {new_status}")


def append_status_note(
    row: dict[str, Any],
    *,
    status: str,
    note: str,
    actor: str | None = None,
    reason: str | None = None,
    at: str | None = None,
) -> None:
    if not note.strip():
        raise ValidationError("Status note must be a non-empty string")
    entry: dict[str, str] = {
        "status": status,
        "note": note.strip(),
        "at": at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    if actor is not None:
        entry["actor"] = actor
    if reason is not None:
        entry["reason"] = reason
    row.setdefault("status_notes", [])
    row["status_notes"].append(entry)


def assert_mutable_document(row: dict[str, Any], *, label: str, document_id: str) -> None:
    if row.get("immutable"):
        raise ValidationError(f"{label} {document_id} is immutable and may only be changed via sync")


def apply_status_transition(
    row: dict[str, Any],
    *,
    new_status: str,
    note: str | None = None,
    actor: str | None = None,
    reason: str | None = None,
) -> None:
    current_status = row.get("status", "draft")
    validate_transition(current_status, new_status)
    row["status"] = new_status
    if note is not None:
        append_status_note(row, status=new_status, note=note, actor=actor, reason=reason)
