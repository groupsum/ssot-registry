from __future__ import annotations

import argparse

from ssot_registry.api import freeze_boundary


def register_boundary(subparsers: argparse._SubParsersAction) -> None:
    boundary = subparsers.add_parser("boundary", help="Boundary operations.")
    boundary_sub = boundary.add_subparsers(dest="boundary_command", required=True)

    freeze = boundary_sub.add_parser("freeze", help="Freeze a boundary and emit a snapshot.")
    freeze.add_argument("path", nargs="?", default=".", help="Registry file path or repository root.")
    freeze.add_argument("--boundary-id", default=None, help="Boundary id. Defaults to the active boundary.")
    freeze.set_defaults(func=run_freeze)


def run_freeze(args: argparse.Namespace) -> dict[str, object]:
    return freeze_boundary(path=args.path, boundary_id=args.boundary_id)
