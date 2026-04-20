from __future__ import annotations

import argparse

from ssot_registry.api import export_registry


def register_registry(subparsers: argparse._SubParsersAction) -> None:
    registry = subparsers.add_parser(
        "registry",
        help="Export the full registry in operator-friendly formats.",
        description="Render the complete SSOT registry for interchange, audits, or downstream analysis.",
    )
    registry_sub = registry.add_subparsers(dest="registry_command", required=True)

    export = registry_sub.add_parser(
        "export",
        help="Serialize the entire registry document.",
        description="Export the full registry into a machine-readable or operator-readable format.",
    )
    export.add_argument("path", nargs="?", default=".", help="Repository root or registry file to export from.")
    export.add_argument("--format", required=True, choices=["json", "csv", "df", "yaml", "toml"], help="Output format to write.")
    export.add_argument("--output", default=None, help="Destination file path. Defaults under `.ssot/exports`.")
    export.set_defaults(func=run_export)


def run_export(args: argparse.Namespace) -> dict[str, object]:
    return export_registry(path=args.path, output_format=args.format, output=args.output)
