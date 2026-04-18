from __future__ import annotations

import csv
import io
import json
from typing import Any


def _scalar_to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float, str)):
        return str(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _flatten_row(row: dict[str, Any]) -> dict[str, str]:
    return {key: _scalar_to_text(value) for key, value in row.items()}


def _rows_from_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list) and all(isinstance(item, dict) for item in payload):
        return payload
    if isinstance(payload, dict):
        for key in ("entities", "nodes", "edges"):
            value = payload.get(key)
            if isinstance(value, list) and all(isinstance(item, dict) for item in value):
                return value
        return [payload]
    return [{"value": payload}]


def _render_csv(payload: Any) -> str:
    rows = _rows_from_payload(payload)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(_flatten_row(row))
    return buffer.getvalue()


def _render_table(payload: Any) -> str:
    rows = [_flatten_row(row) for row in _rows_from_payload(payload)]
    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    widths = {col: len(col) for col in columns}
    for row in rows:
        for col in columns:
            widths[col] = max(widths[col], len(row.get(col, "")))

    header = " | ".join(col.ljust(widths[col]) for col in columns)
    divider = "-+-".join("-" * widths[col] for col in columns)
    body = [" | ".join(row.get(col, "").ljust(widths[col]) for col in columns) for row in rows]
    return "\n".join([header, divider, *body]) + "\n"


def _yaml_quote(text: str) -> str:
    escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def _render_yaml(value: Any, indent: int = 0) -> str:
    prefix = "  " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.append(_render_yaml(item, indent + 1))
            else:
                lines.append(f"{prefix}{key}: {_yaml_quote(_scalar_to_text(item))}")
        return "\n".join(lines)
    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}-")
                lines.append(_render_yaml(item, indent + 1))
            else:
                lines.append(f"{prefix}- {_yaml_quote(_scalar_to_text(item))}")
        return "\n".join(lines)
    return f"{prefix}{_yaml_quote(_scalar_to_text(value))}"


def _toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        return f'"{escaped}"'
    if value is None:
        return '""'
    if isinstance(value, list):
        if all(not isinstance(item, (dict, list)) for item in value):
            return "[" + ", ".join(_toml_value(item) for item in value) + "]"
    return _toml_value(json.dumps(value, ensure_ascii=False, sort_keys=True))


def _render_toml(payload: Any) -> str:
    if not isinstance(payload, dict):
        return f"value = {_toml_value(payload)}\n"

    scalars: list[str] = []
    nested: list[tuple[str, Any]] = []
    for key, value in payload.items():
        if isinstance(value, dict):
            nested.append((key, value))
        elif isinstance(value, list) and value and all(isinstance(item, dict) for item in value):
            nested.append((key, value))
        else:
            scalars.append(f"{key} = {_toml_value(value)}")

    lines = scalars[:]
    for key, value in nested:
        if isinstance(value, dict):
            lines.append("")
            lines.append(f"[{key}]")
            lines.append(_render_toml(value).strip())
        else:
            for item in value:
                lines.append("")
                lines.append(f"[[{key}]]")
                lines.append(_render_toml(item).strip())
    return "\n".join(line for line in lines if line is not None).rstrip() + "\n"


def render_payload(payload: Any, output_format: str) -> str:
    if isinstance(payload, dict) and "__rows_only__" in payload:
        payload = payload["__rows_only__"]
    normalized = output_format.lower()
    if normalized == "json":
        return json.dumps(payload, indent=2, sort_keys=False) + "\n"
    if normalized == "csv":
        return _render_csv(payload)
    if normalized in {"df", "dataframe", "table"}:
        return _render_table(payload)
    if normalized == "yaml":
        return _render_yaml(payload) + "\n"
    if normalized == "toml":
        return _render_toml(payload)
    raise ValueError(f"Unsupported output format: {output_format}")
