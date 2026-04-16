from __future__ import annotations

from typing import Any

from ssot_registry.guards.document_lifecycle import append_status_note, assert_mutable_document
from ssot_registry.util.errors import ValidationError


def _walk_supersedes(start_id: str, rows: dict[str, dict[str, Any]]) -> set[str]:
    seen: set[str] = set()
    stack = [start_id]
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        row = rows.get(current, {})
        refs = row.get("supersedes", [])
        if isinstance(refs, list):
            for ref_id in refs:
                if isinstance(ref_id, str):
                    stack.append(ref_id)
    return seen


def apply_supersession(
    rows: dict[str, dict[str, Any]],
    *,
    source_id: str,
    target_ids: list[str],
    label: str,
    note: str | None = None,
) -> None:
    if source_id not in rows:
        raise ValidationError(f"Unknown {label} id: {source_id}")
    source = rows[source_id]
    assert_mutable_document(source, label=label, document_id=source_id)

    deduped_targets: list[str] = []
    seen_targets: set[str] = set()
    for target_id in target_ids:
        if target_id in seen_targets:
            continue
        deduped_targets.append(target_id)
        seen_targets.add(target_id)

    if not deduped_targets:
        raise ValidationError("At least one superseded id is required")

    if source.get("status") != "accepted":
        source["status"] = "accepted"

    source.setdefault("supersedes", [])
    source.setdefault("superseded_by", [])
    source.setdefault("status_notes", [])

    for target_id in deduped_targets:
        if target_id not in rows:
            raise ValidationError(f"Unknown {label} id in --supersedes: {target_id}")
        if target_id == source_id:
            raise ValidationError("A document cannot supersede itself")
        target = rows[target_id]
        assert_mutable_document(target, label=label, document_id=target_id)

        # no cycles through existing supersedes edges
        reachable = _walk_supersedes(target_id, rows)
        if source_id in reachable:
            raise ValidationError(f"Supersession would create a cycle between {source_id} and {target_id}")

        target.setdefault("superseded_by", [])
        target.setdefault("supersedes", [])
        target.setdefault("status_notes", [])
        if target_id not in source["supersedes"]:
            source["supersedes"].append(target_id)
        if source_id not in target["superseded_by"]:
            target["superseded_by"].append(source_id)
        target["status"] = "superseded"
        if note is not None:
            append_status_note(target, status="superseded", note=note)

    if note is not None:
        append_status_note(source, status=source["status"], note=note)
