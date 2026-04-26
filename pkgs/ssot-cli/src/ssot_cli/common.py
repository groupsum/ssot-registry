from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def add_path_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Repository root or registry file to operate on. Defaults to the current directory.",
    )


def add_id_argument(parser: argparse.ArgumentParser, flag: str = "--id", *, dest: str | None = None, help_text: str = "Normalized id.") -> None:
    parser.add_argument(flag, dest=dest, required=True, help=help_text)


def add_ids_argument(parser: argparse.ArgumentParser, flag: str = "--ids", *, dest: str | None = None, help_text: str = "Normalized ids.") -> None:
    parser.add_argument(flag, dest=dest, nargs="+", default=None, help=help_text)


def add_optional_bool_argument(
    parser: argparse.ArgumentParser,
    name: str,
    *,
    dest: str | None = None,
    default: bool | None = None,
    help_text: str,
) -> None:
    parser.add_argument(name, dest=dest, action=argparse.BooleanOptionalAction, default=default, help=help_text)


def compact_dict(values: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in values.items() if value is not None}


def collect_list_fields(args: argparse.Namespace, mapping: dict[str, str]) -> dict[str, list[str]]:
    links: dict[str, list[str]] = {}
    for attr_name, field_name in mapping.items():
        value = getattr(args, attr_name)
        if value:
            links[field_name] = value
    return links


def load_json_object_argument(
    *,
    inline_value: str | None,
    file_value: str | None,
    label: str,
) -> dict[str, Any] | None:
    if inline_value is None and file_value is None:
        return None
    if inline_value is not None and file_value is not None:
        raise ValueError(f"{label} accepts only one of inline JSON or JSON file")
    if file_value is not None:
        raw_text = Path(file_value).read_text(encoding="utf-8")
    else:
        raw_text = inline_value or ""
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} must be valid JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must decode to a JSON object")
    return payload
