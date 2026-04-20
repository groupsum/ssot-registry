from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ssot_contracts import load_schema_text
from ssot_contracts.generated.python.enums import SCHEMA_VERSION
from ssot_registry.model.document import DOCUMENT_ORIGINS, DOCUMENT_SLUG_PATTERN, DOCUMENT_STATUSES, SPEC_KINDS
from ssot_registry.model.schema_version import is_semver_schema_version
from ssot_registry.util.errors import ValidationError
from ssot_registry.util.jsonio import stable_json_dumps


SECTION_HEADING_PATTERN = re.compile(r"^## (?P<title>.+?)\s*$")
_INTEGER_PATTERN = re.compile(r"^-?(0|[1-9]\d*)$")
_DOCUMENT_SCHEMA_CACHE: dict[str, dict[str, Any]] = {}


def normalize_section_key(title: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", title.strip().lower()).strip("_")
    return normalized or "content"


def build_document_summary(body: str, fallback: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if stripped and not re.match(r"^(?:[-*]|\d+\.)\s+", stripped):
            return stripped
    return fallback


def build_body_from_sections(kind: str, sections: dict[str, list[str]]) -> str:
    ordered_keys = [
        key
        for key, values in sections.items()
        if key != "consequences" and isinstance(values, list) and any(isinstance(value, str) and value.strip() for value in values)
    ]
    if not ordered_keys:
        return ""

    body_parts: list[str] = []
    for key in ordered_keys:
        values = sections[key]
        content = "\n\n".join(value.strip() for value in values if isinstance(value, str) and value.strip()).strip()
        if not content:
            continue
        if len(ordered_keys) == 1 and ((kind == "adr" and key == "decision") or (kind == "spec" and key == "content")):
            body_parts.append(content)
        else:
            body_parts.append(f"## {key.replace('_', ' ').title()}\n\n{content}")
    return "\n\n".join(body_parts).strip()


def document_body_from_payload(kind: str, payload: dict[str, Any]) -> str:
    body = payload.get("body")
    if isinstance(body, str) and body.strip():
        return body.strip()
    sections = payload.get("sections")
    if isinstance(sections, dict):
        body = build_body_from_sections(kind, sections)
        if body:
            return body
    raise ValidationError("Document body must be a non-empty string")


def normalize_document_payload(kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    normalized["body"] = document_body_from_payload(kind, normalized)
    normalized.pop("sections", None)
    if kind == "spec":
        normalized.setdefault("adr_ids", [])
    fallback_title = normalized.get("title")
    normalized["summary"] = build_document_summary(
        normalized["body"],
        fallback_title if isinstance(fallback_title, str) and fallback_title.strip() else "",
    )
    return normalized


def parse_markdown_document(kind: str, text: str, *, fallback_title: str) -> tuple[str, str | None, str]:
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
    body = build_body_from_sections(kind, sections)

    return title, extracted_status, body


def build_document_payload(kind: str, row: dict[str, Any], body: str) -> dict[str, Any]:
    normalized_body = body.strip()
    payload: dict[str, Any] = {
        "schema_version": row.get("minimum_schema_version") or row.get("schema_version") or SCHEMA_VERSION,
        "kind": kind,
        "id": row["id"],
        "number": row["number"],
        "slug": row["slug"],
        "title": row["title"],
        "status": row["status"],
        "origin": row["origin"],
        "decision_date": None,
        "tags": [],
        "summary": build_document_summary(normalized_body, row["title"]),
        "supersedes": list(row.get("supersedes", [])),
        "superseded_by": list(row.get("superseded_by", [])),
        "status_notes": list(row.get("status_notes", [])),
        "references": [],
        "body": normalized_body,
    }
    if kind == "spec":
        payload["spec_kind"] = row.get("kind", "local-policy")
        payload["adr_ids"] = list(row.get("adr_ids", []))
    return payload


def _dump_json_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _dump_block_scalar(value: str, indent: int) -> list[str]:
    prefix = "  " * indent
    lines = value.splitlines()
    if not lines:
        return [prefix]
    return [f"{prefix}{line}" if line else prefix for line in lines]


def _dump_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        return str(value)
    if isinstance(value, str):
        return _dump_json_string(value)
    raise TypeError(f"Unsupported scalar value for YAML rendering: {value!r}")


def _dump_yaml_lines(value: Any, indent: int = 0) -> list[str]:
    prefix = "  " * indent
    if isinstance(value, dict):
        if not value:
            return [f"{prefix}{{}}"]
        lines: list[str] = []
        for key, item in value.items():
            if isinstance(item, dict):
                if item:
                    lines.append(f"{prefix}{key}:")
                    lines.extend(_dump_yaml_lines(item, indent + 1))
                else:
                    lines.append(f"{prefix}{key}: {{}}")
                continue
            if isinstance(item, list):
                if item:
                    lines.append(f"{prefix}{key}:")
                    lines.extend(_dump_yaml_lines(item, indent + 1))
                else:
                    lines.append(f"{prefix}{key}: []")
                continue
            if isinstance(item, str) and (key == "body" or "\n" in item):
                lines.append(f"{prefix}{key}: |-")
                lines.extend(_dump_block_scalar(item, indent + 1))
                continue
            lines.append(f"{prefix}{key}: {_dump_scalar(item)}")
        return lines

    if isinstance(value, list):
        if not value:
            return [f"{prefix}[]"]
        lines = []
        for item in value:
            if isinstance(item, dict):
                if item:
                    lines.append(f"{prefix}-")
                    lines.extend(_dump_yaml_lines(item, indent + 1))
                else:
                    lines.append(f"{prefix}- {{}}")
                continue
            if isinstance(item, list):
                if item:
                    lines.append(f"{prefix}-")
                    lines.extend(_dump_yaml_lines(item, indent + 1))
                else:
                    lines.append(f"{prefix}- []")
                continue
            if isinstance(item, str) and "\n" in item:
                lines.append(f"{prefix}- |-")
                lines.extend(_dump_block_scalar(item, indent + 1))
                continue
            lines.append(f"{prefix}- {_dump_scalar(item)}")
        return lines

    return [f"{prefix}{_dump_scalar(value)}"]


def dump_document_yaml(payload: dict[str, Any]) -> str:
    return "\n".join(_dump_yaml_lines(payload)) + "\n"


def dump_document_text(payload: dict[str, Any], path: str | Path) -> str:
    suffix = Path(path).suffix.lower()
    if suffix == ".json":
        return stable_json_dumps(payload)
    return dump_document_yaml(payload)


class _YamlSubsetParser:
    def __init__(self, text: str) -> None:
        self.lines = text.replace("\r\n", "\n").split("\n")
        self.index = 0

    def parse(self) -> Any:
        self._skip_blank_lines()
        if self.index >= len(self.lines):
            raise ValidationError("Document is empty")
        value = self._parse_block(0)
        self._skip_blank_lines()
        if self.index < len(self.lines):
            raise ValidationError(f"Unexpected trailing YAML content at line {self.index + 1}")
        return value

    def _skip_blank_lines(self) -> None:
        while self.index < len(self.lines) and not self.lines[self.index].strip():
            self.index += 1

    def _current_indent(self) -> int:
        line = self.lines[self.index]
        return len(line) - len(line.lstrip(" "))

    def _parse_block(self, indent: int) -> Any:
        self._skip_blank_lines()
        if self.index >= len(self.lines):
            raise ValidationError("Expected YAML content")
        current_indent = self._current_indent()
        if current_indent != indent:
            raise ValidationError(f"Unexpected indentation at line {self.index + 1}")
        stripped = self.lines[self.index][indent:]
        if stripped.startswith("-"):
            return self._parse_list(indent)
        return self._parse_mapping(indent)

    def _parse_mapping(self, indent: int) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        while self.index < len(self.lines):
            line = self.lines[self.index]
            if not line.strip():
                self.index += 1
                continue
            current_indent = self._current_indent()
            if current_indent < indent:
                break
            if current_indent > indent:
                raise ValidationError(f"Unexpected indentation at line {self.index + 1}")
            stripped = line[indent:]
            if stripped.startswith("-"):
                raise ValidationError(f"Expected mapping entry at line {self.index + 1}")
            if ":" not in stripped:
                raise ValidationError(f"Expected mapping entry at line {self.index + 1}")
            key, rest = stripped.split(":", 1)
            key = key.strip()
            if not key:
                raise ValidationError(f"Missing mapping key at line {self.index + 1}")
            self.index += 1
            value_text = rest.lstrip()
            if value_text in {"|-", "|"}:
                payload[key] = self._parse_block_scalar(indent + 2)
            elif value_text:
                payload[key] = self._parse_scalar(value_text)
            else:
                payload[key] = self._parse_nested(indent + 2)
        return payload

    def _parse_list(self, indent: int) -> list[Any]:
        items: list[Any] = []
        while self.index < len(self.lines):
            line = self.lines[self.index]
            if not line.strip():
                self.index += 1
                continue
            current_indent = self._current_indent()
            if current_indent < indent:
                break
            if current_indent > indent:
                raise ValidationError(f"Unexpected indentation at line {self.index + 1}")
            stripped = line[indent:]
            if not stripped.startswith("-"):
                break
            self.index += 1
            value_text = stripped[1:].lstrip()
            if value_text in {"|-", "|"}:
                items.append(self._parse_block_scalar(indent + 2))
            elif value_text:
                items.append(self._parse_scalar(value_text))
            else:
                items.append(self._parse_nested(indent + 2))
        return items

    def _parse_nested(self, indent: int) -> Any:
        self._skip_blank_lines()
        if self.index >= len(self.lines):
            raise ValidationError("Expected nested YAML block")
        if self._current_indent() < indent:
            raise ValidationError(f"Expected nested YAML block at line {self.index + 1}")
        return self._parse_block(indent)

    def _parse_block_scalar(self, indent: int) -> str:
        values: list[str] = []
        while self.index < len(self.lines):
            line = self.lines[self.index]
            if not line.strip():
                if self.index == len(self.lines) - 1:
                    break
                values.append("")
                self.index += 1
                continue
            current_indent = self._current_indent()
            if current_indent < indent:
                break
            values.append(line[indent:])
            self.index += 1
        return "\n".join(values)

    def _parse_scalar(self, value_text: str) -> Any:
        if value_text == "null":
            return None
        if value_text == "true":
            return True
        if value_text == "false":
            return False
        if value_text == "[]":
            return []
        if value_text == "{}":
            return {}
        if _INTEGER_PATTERN.match(value_text):
            return int(value_text)
        if value_text.startswith('"'):
            try:
                return json.loads(value_text)
            except json.JSONDecodeError as exc:
                raise ValidationError(f"Invalid YAML string scalar {value_text!r}") from exc
        return value_text


def load_document_yaml(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    stripped = text.lstrip("\ufeff").strip()
    try:
        if stripped.startswith(("{", "[")):
            payload = json.loads(stripped)
        else:
            payload = _YamlSubsetParser(text).parse()
    except (ValidationError, json.JSONDecodeError) as exc:
        raise ValidationError(f"Document is not valid YAML/JSON content: {path.as_posix()}") from exc
    if not isinstance(payload, dict):
        raise ValidationError(f"Document payload must be an object: {path.as_posix()}")
    return payload


def _load_document_schema(kind: str) -> dict[str, Any]:
    if kind not in _DOCUMENT_SCHEMA_CACHE:
        schema_name = "adr.schema.json" if kind == "adr" else "spec.schema.json"
        _DOCUMENT_SCHEMA_CACHE[kind] = json.loads(load_schema_text(schema_name))
    return _DOCUMENT_SCHEMA_CACHE[kind]


def _resolve_schema_ref(root_schema: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValidationError(f"Unsupported schema reference: {ref}")
    current: Any = root_schema
    for part in ref[2:].split("/"):
        if not isinstance(current, dict) or part not in current:
            raise ValidationError(f"Unable to resolve schema reference: {ref}")
        current = current[part]
    if not isinstance(current, dict):
        raise ValidationError(f"Schema reference did not resolve to an object: {ref}")
    return current


def _schema_type_matches(value: Any, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "null":
        return value is None
    raise ValidationError(f"Unsupported schema type: {expected_type}")


def _schema_pointer(pointer: str, key: str) -> str:
    return f"{pointer}.{key}" if key.isidentifier() else f"{pointer}[{key!r}]"


def _validate_schema(instance: Any, schema: dict[str, Any], *, root_schema: dict[str, Any], pointer: str) -> None:
    if "$ref" in schema:
        _validate_schema(instance, _resolve_schema_ref(root_schema, str(schema["$ref"])), root_schema=root_schema, pointer=pointer)
        return

    expected_type = schema.get("type")
    if isinstance(expected_type, str):
        expected_types = [expected_type]
    elif isinstance(expected_type, list):
        expected_types = [str(item) for item in expected_type]
    else:
        expected_types = []

    if expected_types and not any(_schema_type_matches(instance, item) for item in expected_types):
        raise ValidationError(f"{pointer} must be of type {expected_types}")

    if "const" in schema and instance != schema["const"]:
        raise ValidationError(f"{pointer} must equal {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        raise ValidationError(f"{pointer} must be one of {list(schema['enum'])}")

    if isinstance(instance, str):
        min_length = schema.get("minLength")
        if isinstance(min_length, int) and len(instance) < min_length:
            raise ValidationError(f"{pointer} must have length >= {min_length}")
        max_length = schema.get("maxLength")
        if isinstance(max_length, int) and len(instance) > max_length:
            raise ValidationError(f"{pointer} must have length <= {max_length}")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.match(pattern, instance) is None:
            raise ValidationError(f"{pointer} must match pattern {pattern!r}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        minimum = schema.get("minimum")
        if isinstance(minimum, (int, float)) and instance < minimum:
            raise ValidationError(f"{pointer} must be >= {minimum}")

    if isinstance(instance, list):
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(instance) < min_items:
            raise ValidationError(f"{pointer} must contain at least {min_items} item(s)")
        items_schema = schema.get("items")
        if isinstance(items_schema, dict):
            for index, item in enumerate(instance):
                _validate_schema(item, items_schema, root_schema=root_schema, pointer=f"{pointer}[{index}]")

    if isinstance(instance, dict):
        min_properties = schema.get("minProperties")
        if isinstance(min_properties, int) and len(instance) < min_properties:
            raise ValidationError(f"{pointer} must contain at least {min_properties} propertie(s)")

        required = schema.get("required", [])
        if isinstance(required, list):
            missing = [str(key) for key in required if key not in instance]
            if missing:
                raise ValidationError(f"{pointer} is missing required field(s): {', '.join(missing)}")

        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            properties = {}
        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            key_pointer = _schema_pointer(pointer, key)
            if key in properties and isinstance(properties[key], dict):
                _validate_schema(value, properties[key], root_schema=root_schema, pointer=key_pointer)
                continue
            if additional is False:
                raise ValidationError(f"{pointer} does not allow additional property {key!r}")
            if isinstance(additional, dict):
                _validate_schema(value, additional, root_schema=root_schema, pointer=key_pointer)


def _validate_document_schema(kind: str, payload: dict[str, Any]) -> None:
    schema = _load_document_schema(kind)
    _validate_schema(payload, schema, root_schema=schema, pointer="$")


def validate_document_payload(kind: str, payload: dict[str, Any], *, expected_row: dict[str, Any] | None = None) -> None:
    _validate_document_schema(kind, payload)

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
        "body",
    }
    missing = sorted(field for field in required if field not in payload)
    if missing:
        raise ValidationError(f"Document payload missing required fields: {', '.join(missing)}")
    if payload.get("kind") != kind:
        raise ValidationError(f"Document kind must be {kind}")
    if not is_semver_schema_version(payload.get("schema_version")):
        raise ValidationError("Document schema_version must be a semver string like 0.1.0")
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
    body = payload.get("body")
    if not isinstance(body, str) or not body.strip():
        raise ValidationError("Document body must be a non-empty string")
    if kind == "spec":
        spec_kind = payload.get("spec_kind")
        if spec_kind not in SPEC_KINDS:
            raise ValidationError(f"SPEC documents must use spec_kind from {sorted(SPEC_KINDS)}")
        adr_ids = payload.get("adr_ids", [])
        if not isinstance(adr_ids, list) or not all(isinstance(item, str) for item in adr_ids):
            raise ValidationError("SPEC documents must use adr_ids as a list of strings")

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
        if kind == "spec" and payload.get("adr_ids", []) != expected_row.get("adr_ids", []):
            raise ValidationError(
                f"Document field adr_ids does not match registry row: expected {expected_row.get('adr_ids', [])!r}"
            )
