from __future__ import annotations

import argparse

from ssot_registry.api import upgrade_registry


def register_upgrade(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("upgrade", help="Upgrade a repository registry to the installed schema and package version.")
    parser.add_argument("path", nargs="?", default=".", help="Registry file path or repository root.")
    parser.add_argument("--target-version", default=None, help="Package version to upgrade to. Defaults to the installed version.")
    parser.add_argument("--sync-docs", action="store_true", help="Sync packaged ADRs and specs after schema migration.")
    parser.add_argument("--write-report", action="store_true", help="Write upgrade report under .ssot/reports.")
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> dict[str, object]:
    return upgrade_registry(
        args.path,
        target_version=args.target_version,
        sync_docs=args.sync_docs,
        write_report=args.write_report,
    )
