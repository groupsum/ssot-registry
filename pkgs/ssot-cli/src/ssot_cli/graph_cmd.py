from __future__ import annotations

import argparse

from ssot_registry.api import export_graph


def register_graph(subparsers: argparse._SubParsersAction) -> None:
    graph = subparsers.add_parser(
        "graph",
        help="Export relationship views of the registry.",
        description="Generate graph representations of registry entities and their links for review or visualization.",
    )
    graph_sub = graph.add_subparsers(dest="graph_command", required=True)

    export = graph_sub.add_parser(
        "export",
        help="Render the registry relationship graph.",
        description="Export a graph view of the current registry for tooling, diagrams, or visual inspection.",
    )
    export.add_argument("path", nargs="?", default=".", help="Repository root or registry file to export from.")
    export.add_argument("--format", required=True, choices=["json", "dot", "png", "svg"], help="Graph serialization or image format to emit.")
    export.add_argument("--output", default=None, help="Destination file path. Defaults under `.ssot/graphs`.")
    export.set_defaults(func=run_export)


def run_export(args: argparse.Namespace) -> dict[str, object]:
    return export_graph(path=args.path, output_format=args.format, output=args.output)
