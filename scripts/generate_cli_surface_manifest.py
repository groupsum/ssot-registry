#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
CORE_SRC_DIR = REPO_ROOT / "pkgs" / "ssot-core" / "src"
CONTRACTS_SRC_DIR = REPO_ROOT / "pkgs" / "ssot-contracts" / "src"
VIEWS_SRC_DIR = REPO_ROOT / "pkgs" / "ssot-views" / "src"
CODEGEN_SRC_DIR = REPO_ROOT / "pkgs" / "ssot-codegen" / "src"
CLI_SRC_DIR = REPO_ROOT / "pkgs" / "ssot-cli" / "src"
for path in (CORE_SRC_DIR, CODEGEN_SRC_DIR, VIEWS_SRC_DIR, CONTRACTS_SRC_DIR, CLI_SRC_DIR, SRC_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ssot_cli.main import build_parser


def _build_root_parser() -> argparse.ArgumentParser:
    return build_parser(prog="ssot-registry")


def _option_flags(parser: argparse.ArgumentParser) -> list[str]:
    flags: list[str] = []
    for action in parser._actions:
        if isinstance(action, argparse._HelpAction):
            continue
        if not action.option_strings:
            continue
        for option in action.option_strings:
            if option not in flags:
                flags.append(option)
    return sorted(flags)


def _walk_parser(
    parser: argparse.ArgumentParser,
    path: list[str],
    command_paths: list[str],
    flags_by_path: dict[str, list[str]],
) -> None:
    if path:
        path_key = " ".join(path)
        command_paths.append(path_key)
        flags_by_path[path_key] = _option_flags(parser)

    for action in parser._actions:
        if not isinstance(action, argparse._SubParsersAction):
            continue
        for name, child_parser in sorted(action.choices.items()):
            _walk_parser(child_parser, [*path, name], command_paths, flags_by_path)


def generate_manifest() -> dict[str, Any]:
    root = _build_root_parser()

    top_level_commands: list[str] = []
    for action in root._actions:
        if isinstance(action, argparse._SubParsersAction):
            top_level_commands = sorted(action.choices.keys())
            break

    command_paths: list[str] = []
    flags_by_path: dict[str, list[str]] = {}
    _walk_parser(root, [], command_paths, flags_by_path)

    return {
        "top_level_commands": top_level_commands,
        "subcommand_paths": sorted(command_paths),
        "global_flags": _option_flags(root),
        "flags_by_path": {key: flags_by_path[key] for key in sorted(flags_by_path)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a JSON manifest for the ssot-registry CLI command surface.")
    parser.add_argument(
        "--output",
        default=str(REPO_ROOT / "tests/fixtures/cli_surface_manifest.json"),
        help="Path to write the generated manifest JSON.",
    )
    args = parser.parse_args()

    manifest = generate_manifest()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Wrote CLI surface manifest to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
