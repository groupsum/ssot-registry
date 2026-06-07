from __future__ import annotations

import argparse

from ssot_registry.api import export_graph, export_lineage_graph


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

    lineage = graph_sub.add_parser(
        "lineage",
        help="Render a self-contained interactive lineage graph.",
        description="Export an HTML graph viewer with network and top-down lineage modes for local SSOT registry review.",
    )
    lineage.add_argument("path", nargs="?", default=".", help="Repository root or registry file to render from.")
    lineage.add_argument("--output", default=None, help="Destination HTML file. Defaults under `.ssot/graphs`.")
    lineage.set_defaults(func=run_lineage)


def run_export(args: argparse.Namespace) -> dict[str, object]:
    return export_graph(path=args.path, output_format=args.format, output=args.output)


def run_lineage(args: argparse.Namespace) -> dict[str, object]:
    return export_lineage_graph(path=args.path, output=args.output)
