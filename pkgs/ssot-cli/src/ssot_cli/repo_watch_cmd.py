from __future__ import annotations

import argparse
from pathlib import Path

from ssot_registry.watch.observer import scan_repo


def register_repo_watch(subparsers: argparse._SubParsersAction) -> None:
    watch = subparsers.add_parser("repo-watch", help="Scan the worktree for changed, forbidden, or out-of-lease paths.")
    watch_sub = watch.add_subparsers(dest="repo_watch_command", required=True)

    scan = watch_sub.add_parser("scan", help="Run one repo-watch scan and optionally emit control-plane events.")
    scan.add_argument("path", nargs="?", default=".")
    scan.add_argument("--no-emit-events", action="store_true")
    scan.set_defaults(func=run_scan)


def run_scan(args: argparse.Namespace) -> dict[str, object]:
    return scan_repo(Path(args.path), emit_events=not args.no_emit_events)
