from __future__ import annotations

import argparse
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
