from __future__ import annotations

import argparse

from ssot_registry.api import export_graph


def register_graph(subparsers: argparse._SubParsersAction) -> None:
    graph = subparsers.add_parser("graph", help="Graph export operations.")
    graph_sub = graph.add_subparsers(dest="graph_command", required=True)

    export = graph_sub.add_parser("export", help="Export the registry graph.")
    export.add_argument("path", nargs="?", default=".", help="Registry file path or repository root.")
    export.add_argument("--format", required=True, choices=["json", "dot"], help="Graph export format.")
    export.add_argument("--output", default=None, help="Output path. Defaults under .ssot/graphs.")
    export.set_defaults(func=run_export)


def run_export(args: argparse.Namespace) -> dict[str, object]:
    return export_graph(path=args.path, output_format=args.format, output=args.output)
