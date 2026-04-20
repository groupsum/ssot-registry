from __future__ import annotations

import argparse

from ssot_registry.api import upgrade_registry


def register_upgrade(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "upgrade",
        help="Migrate a repository to the installed SSOT schema.",
        description="Upgrade registry structure and packaged metadata to match the installed SSOT toolchain version.",
    )
    parser.add_argument("path", nargs="?", default=".", help="Repository root or registry file to upgrade.")
    parser.add_argument("--target-version", default=None, help="Explicit package version target. Defaults to the installed version.")
    parser.add_argument("--sync-docs", action="store_true", help="Refresh packaged ADR and SPEC documents after the migration completes.")
    parser.add_argument("--write-report", action="store_true", help="Write an upgrade report under `.ssot/reports`.")
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> dict[str, object]:
    return upgrade_registry(
        args.path,
        target_version=args.target_version,
        sync_docs=args.sync_docs,
        write_report=args.write_report,
    )
