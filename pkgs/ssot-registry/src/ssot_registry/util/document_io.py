from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ssot_registry.model.document import DOCUMENT_ORIGINS, DOCUMENT_SLUG_PATTERN, DOCUMENT_STATUSES, SPEC_KINDS
from ssot_registry.util.errors import ValidationError
from ssot_registry.util.jsonio import stable_json_dumps


SECTION_HEADING_PATTERN = re.compile(r"^## (?P<title>.+?)\s*$")


def normalize_section_key(title: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", title.strip().lower()).strip("_")
    return normalized or "content"


def build_document_summary(sections: dict[str, list[str]], fallback: str) -> str:
    for values in sections.values():
        for value in values:
            for line in value.splitlines():
                stripped = line.strip()
                if stripped and not stripped.startswith(("-", "*", "1.", "2.", "3.")):
                    return stripped
    return fallback


def parse_markdown_document(kind: str, text: str, *, fallback_title: str) -> tuple[str, str | None, dict[str, list[str]]]:
    lines = text.replace("\r\n", "\n").split("\n")
    title = fallback_title
    start_index = 0

    for index, raw_line in enumerate(lines):
        stripped = raw_line.lstrip("\ufeff").strip()
        if not stripped:
            continue
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            if kind == "adr" and title.startswith("ADR-") and ":" in title:
                title = title.split(":", 1)[1].strip()
            elif kind == "spec" and title.startswith("SPEC-") and ":" in title:
                title = title.split(":", 1)[1].strip()
            start_index = index + 1
        break

    sections: dict[str, list[str]] = {}
    current_key: str | None = None
    current_lines: list[str] = []
    extracted_status: str | None = None

    def flush() -> None:
        nonlocal current_key, current_lines, extracted_status
        if current_key is None:
            return
        content = "\n".join(current_lines).strip()
        current_lines = []
        if current_key == "status":
            if content:
                extracted_status = content.splitlines()[0].strip().lower()
            current_key = None
            return
        if content:
            sections.setdefault(current_key, []).append(content)
        current_key = None

    for raw_line in lines[start_index:]:
        match = SECTION_HEADING_PATTERN.match(raw_line.strip())
        if match is not None:
            flush()
            current_key = normalize_section_key(match.group("title"))
            continue
        if current_key == "status" and current_lines and not raw_line.strip():
            flush()
            continue
        if current_key is None:
            current_key = "decision" if kind == "adr" else "content"
        current_lines.append(raw_line)
    flush()

    if kind == "adr" and "decision" not in sections:
        fallback = sections.pop("content", [])
        if fallback:
            sections["decision"] = fallback
    if kind == "spec" and not sections:
        body = "\n".join(lines[start_index:]).strip()
        if body:
            sections["content"] = [body]

    return title, extracted_status, sections


def build_document_payload(kind: str, row: dict[str, Any], sections: dict[str, list[str]]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": row.get("minimum_schema_version") or row.get("schema_version") or 9,
        "kind": kind,
        "id": row["id"],
        "number": row["number"],
        "slug": row["slug"],
        "title": row["title"],
        "status": row["status"],
        "origin": row["origin"],
        "decision_date": None,
        "tags": [],
        "summary": build_document_summary(sections, row["title"]),
        "supersedes": list(row.get("supersedes", [])),
        "superseded_by": list(row.get("superseded_by", [])),
        "status_notes": list(row.get("status_notes", [])),
        "references": [],
        "sections": sections,
    }
    if kind == "spec":
        payload["spec_kind"] = row.get("kind", "local-policy")
    return payload


def dump_document_yaml(payload: dict[str, Any]) -> str:
    return stable_json_dumps(payload)


def load_document_yaml(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Document is not valid YAML/JSON content: {path.as_posix()}") from exc
    if not isinstance(payload, dict):
        raise ValidationError(f"Document payload must be an object: {path.as_posix()}")
    return payload


def validate_document_payload(kind: str, payload: dict[str, Any], *, expected_row: dict[str, Any] | None = None) -> None:
    required = {
        "schema_version",
        "kind",
        "id",
        "number",
        "slug",
        "title",
        "status",
        "origin",
        "summary",
        "sections",
    }
    missing = sorted(field for field in required if field not in payload)
    if missing:
        raise ValidationError(f"Document payload missing required fields: {', '.join(missing)}")
    if payload.get("kind") != kind:
        raise ValidationError(f"Document kind must be {kind}")
    if not isinstance(payload.get("schema_version"), int) or payload["schema_version"] < 1:
        raise ValidationError("Document schema_version must be an integer >= 1")
    if not isinstance(payload.get("id"), str) or not payload["id"].strip():
        raise ValidationError("Document id must be a non-empty string")
    if not isinstance(payload.get("number"), int) or payload["number"] < 1:
        raise ValidationError("Document number must be an integer >= 1")
    slug = payload.get("slug")
    if not isinstance(slug, str) or DOCUMENT_SLUG_PATTERN.match(slug) is None:
        raise ValidationError("Document slug must match ^[a-z0-9]+(?:-[a-z0-9]+)*$")
    if not isinstance(payload.get("title"), str) or not payload["title"].strip():
        raise ValidationError("Document title must be a non-empty string")
    if payload.get("status") not in DOCUMENT_STATUSES:
        raise ValidationError(f"Document status must be one of {list(DOCUMENT_STATUSES)}")
    if payload.get("origin") not in DOCUMENT_ORIGINS:
        raise ValidationError(f"Document origin must be one of {sorted(DOCUMENT_ORIGINS)}")
    if not isinstance(payload.get("summary"), str) or not payload["summary"].strip():
        raise ValidationError("Document summary must be a non-empty string")
    sections = payload.get("sections")
    if not isinstance(sections, dict) or not sections:
        raise ValidationError("Document sections must be a non-empty object")
    for key, value in sections.items():
        if not isinstance(key, str) or not key.strip():
            raise ValidationError("Document section names must be non-empty strings")
        if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
            raise ValidationError(f"Document section '{key}' must be a non-empty list of non-empty strings")
    if kind == "adr":
        if "decision" not in sections:
            raise ValidationError("ADR documents must contain sections.decision")
    else:
        spec_kind = payload.get("spec_kind")
        if spec_kind not in SPEC_KINDS:
            raise ValidationError(f"SPEC documents must use spec_kind from {sorted(SPEC_KINDS)}")

    for field_name in ("tags", "supersedes", "superseded_by", "references"):
        value = payload.get(field_name, [])
        if value is not None and (not isinstance(value, list) or not all(isinstance(item, str) for item in value)):
            raise ValidationError(f"Document {field_name} must be a list of strings")
    notes = payload.get("status_notes", [])
    if notes is not None and not isinstance(notes, list):
        raise ValidationError("Document status_notes must be a list")

    if expected_row is not None:
        for field_name in ("id", "number", "slug", "title", "status", "origin"):
            if payload.get(field_name) != expected_row.get(field_name):
                raise ValidationError(
                    f"Document field {field_name} does not match registry row: expected {expected_row.get(field_name)!r}"
                )
        if kind == "spec" and payload.get("spec_kind") != expected_row.get("kind"):
            raise ValidationError(
                f"Document field spec_kind does not match registry row: expected {expected_row.get('kind')!r}"
            )
