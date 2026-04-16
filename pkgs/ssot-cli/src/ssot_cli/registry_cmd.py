from __future__ import annotations

import argparse

from ssot_registry.api import export_registry


def register_registry(subparsers: argparse._SubParsersAction) -> None:
    registry = subparsers.add_parser("registry", help="Registry operations.")
    registry_sub = registry.add_subparsers(dest="registry_command", required=True)

    export = registry_sub.add_parser("export", help="Export the full registry document.")
    export.add_argument("path", nargs="?", default=".", help="Registry file path or repository root.")
    export.add_argument("--format", required=True, choices=["json", "csv", "df", "yaml", "toml"], help="Registry export format.")
    export.add_argument("--output", default=None, help="Output path. Defaults under .ssot/exports.")
    export.set_defaults(func=run_export)


def run_export(args: argparse.Namespace) -> dict[str, object]:
    return export_registry(path=args.path, output_format=args.format, output=args.output)
