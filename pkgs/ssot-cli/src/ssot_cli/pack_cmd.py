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
    inspect.add_argument("--manifest", action="store_true", help="Include the full packaged manifest in the response.")
    inspect.set_defaults(func=run_inspect)

    preflight = pack_sub.add_parser("preflight", help="Validate a governance pack before repository mutation.")
    add_path_argument(preflight)
    preflight.add_argument("package", help="Import package name for the governance pack.")
    preflight.add_argument("--kind", choices=["adr", "adrs", "spec", "specs"], default=None)
    preflight.add_argument("--all", action="store_true", help="Check all document kinds declared by the pack.")
    preflight.add_argument("--manifest", action="store_true", help="Include the full packaged manifest in the response.")
    preflight.add_argument("--pin", default=None, help="Require the pack version to match this exact value.")
    preflight.add_argument("--resolved", action="store_true", help="Include resolved manifest document entries in the response.")
    preflight.add_argument("--trusted-only", action="store_true", help="Require the pack to be trusted by default.")
    preflight.set_defaults(func=run_preflight)

    sync = pack_sub.add_parser("sync", help="Sync declared governance-pack documents into a repository.")
    add_path_argument(sync)
    sync.add_argument("package", help="Import package name for the governance pack.")
    sync.add_argument("--kind", choices=["adr", "adrs", "spec", "specs"], default=None)
    sync.add_argument("--all", action="store_true", help="Sync all document kinds declared by the pack.")
    sync.add_argument("--trusted-only", action="store_true", help="Require the pack to be trusted by default.")
    sync.add_argument("--trust", action="store_true", help="Record explicit operator approval for syncing the selected pack.")
    sync.add_argument("--dry-run", action="store_true", help="Report sync changes without writing files or registry rows.")
    sync.add_argument("--manifest", action="store_true", help="Include the full packaged manifest in the response.")
    sync.add_argument("--no-sync", action="store_true", help="Run preflight and return without writing files or registry rows.")
    sync.add_argument("--pin", default=None, help="Require the pack version to match this exact value.")
    sync.add_argument("--preflight-only", action="store_true", help="Run only preflight checks through the sync command surface.")
    sync.add_argument("--prune-stale", action="store_true", help="Remove stale extension-pack rows for this pack after successful sync.")
    sync.add_argument("--reservations", action="store_true", help="Include reservation changes in the response.")
    sync.add_argument("--resolved", action="store_true", help="Include resolved manifest document entries in the response.")
    sync.add_argument("--yes", action="store_true", help="Acknowledge noninteractive operator approval for the requested sync.")
    sync.set_defaults(func=run_sync)


def run_inspect(args: argparse.Namespace) -> dict[str, object]:
    payload = inspect_pack(args.package)
    if not args.manifest:
        payload.pop("documents", None)
    return payload


def run_preflight(args: argparse.Namespace) -> dict[str, object]:
    if args.all and args.kind is not None:
        raise ValueError("--all cannot be combined with --kind")
    return preflight_pack(
        args.path,
        args.package,
        kind=None if args.all else args.kind,
        trusted_only=args.trusted_only,
        pin=args.pin,
        include_manifest=args.manifest,
        include_resolved=args.resolved,
    )


def run_sync(args: argparse.Namespace) -> dict[str, object]:
    if args.all and args.kind is not None:
        raise ValueError("--all cannot be combined with --kind")
    return sync_pack(
        args.path,
        args.package,
        kind=None if args.all else args.kind,
        trusted_only=args.trusted_only,
        dry_run=args.dry_run,
        pin=args.pin,
        preflight_only=args.preflight_only,
        no_sync=args.no_sync,
        prune_stale=args.prune_stale,
        include_manifest=args.manifest,
        include_resolved=args.resolved,
        include_reservations=args.reservations,
        trust=args.trust,
        yes=args.yes,
    )
