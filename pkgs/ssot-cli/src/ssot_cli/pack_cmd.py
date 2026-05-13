from __future__ import annotations

import argparse

from ssot_registry.api import inspect_pack, preflight_pack, sync_pack

from .common import add_path_argument


def register_pack(subparsers: argparse._SubParsersAction) -> None:
    pack = subparsers.add_parser(
        "pack",
        help="Inspect, preflight, and sync governance packs.",
        description="Operate on self-describing SSOT governance packs that expose the shared pack contract.",
    )
    pack_sub = pack.add_subparsers(dest="pack_command", required=True)

    inspect = pack_sub.add_parser("inspect", help="Inspect packaged governance-pack metadata and manifests.")
    inspect.add_argument("package", help="Import package name for the governance pack.")
    inspect.set_defaults(func=run_inspect)

    preflight = pack_sub.add_parser("preflight", help="Validate a governance pack before repository mutation.")
    add_path_argument(preflight)
    preflight.add_argument("package", help="Import package name for the governance pack.")
    preflight.add_argument("--kind", choices=["adr", "adrs", "spec", "specs"], default=None)
    preflight.add_argument("--trusted-only", action="store_true", help="Require the pack to be trusted by default.")
    preflight.set_defaults(func=run_preflight)

    sync = pack_sub.add_parser("sync", help="Sync declared governance-pack documents into a repository.")
    add_path_argument(sync)
    sync.add_argument("package", help="Import package name for the governance pack.")
    sync.add_argument("--kind", choices=["adr", "adrs", "spec", "specs"], default=None)
    sync.add_argument("--trusted-only", action="store_true", help="Require the pack to be trusted by default.")
    sync.add_argument("--dry-run", action="store_true", help="Report sync changes without writing files or registry rows.")
    sync.set_defaults(func=run_sync)


def run_inspect(args: argparse.Namespace) -> dict[str, object]:
    return inspect_pack(args.package)


def run_preflight(args: argparse.Namespace) -> dict[str, object]:
    return preflight_pack(args.path, args.package, kind=args.kind, trusted_only=args.trusted_only)


def run_sync(args: argparse.Namespace) -> dict[str, object]:
    return sync_pack(args.path, args.package, kind=args.kind, trusted_only=args.trusted_only, dry_run=args.dry_run)

