from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

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
    lineage.add_argument("--open", action="store_true", help="Open the generated HTML file with the local platform opener after export.")
    lineage.set_defaults(func=run_lineage)


def run_export(args: argparse.Namespace) -> dict[str, object]:
    return export_graph(path=args.path, output_format=args.format, output=args.output)


def run_lineage(args: argparse.Namespace) -> dict[str, object]:
    payload = export_lineage_graph(path=args.path, output=args.output)
    if args.open:
        output_path = payload.get("output_path")
        if not isinstance(output_path, str) or not output_path:
            raise ValueError("lineage graph export did not return an output_path to open")
        _open_file(Path(output_path))
        payload["opened"] = True
    else:
        payload["opened"] = False
    return payload


def _open_file(path: Path) -> None:
    target = path.resolve()
    if not target.exists():
        raise ValueError(f"Cannot open missing lineage graph artifact: {target}")
    if target.is_dir():
        raise ValueError(f"Cannot open lineage graph artifact because output path is a directory: {target}")

    try:
        if sys.platform.startswith("win"):
            os.startfile(target)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(target)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(["xdg-open", str(target)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError as exc:
        raise ValueError(f"Failed to open lineage graph artifact {target}: {exc}") from exc
