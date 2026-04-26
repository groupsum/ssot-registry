from __future__ import annotations

import argparse

from ssot_registry.api import run_resolved_test_rows
from ssot_cli.common import add_path_argument


def register_conformance(subparsers: argparse._SubParsersAction) -> None:
    conformance = subparsers.add_parser(
        "conformance",
        help="Conformance package, scaffold, and execution operations.",
        description="Operate reusable SSOT conformance discovery, scaffold, pytest execution, and evidence-output flows.",
    )
    conformance_sub = conformance.add_subparsers(dest="conformance_command", required=True)

    profile = conformance_sub.add_parser("profile", help="Profile discovery.", description="List available SSOT conformance profiles and their grouped case families.")
    profile_sub = profile.add_subparsers(dest="conformance_profile_command", required=True)
    profile_list = profile_sub.add_parser("list", help="List conformance profiles.", description="Show built-in SSOT conformance profiles and family counts.")
    add_path_argument(profile_list)
    profile_list.set_defaults(func=run_profile_list)

    discover = conformance_sub.add_parser("discover", help="Discover conformance cases.", description="Resolve selected SSOT conformance profiles into concrete case files and linked SSOT rows.")
    add_path_argument(discover)
    discover.add_argument("--profiles", nargs="*", default=None, help="Conformance profiles or family names to resolve.")
    discover.set_defaults(func=run_discover)

    scaffold = conformance_sub.add_parser("scaffold", help="Plan or apply conformance rows.", description="Plan or create missing conformance feature, claim, evidence, and test rows in a target SSOT repo.")
    add_path_argument(scaffold)
    scaffold.add_argument("--profiles", nargs="*", default=None, help="Conformance profiles or family names to scaffold.")
    scaffold.add_argument("--apply", action="store_true", help="Create missing rows instead of only reporting the dry-run plan.")
    scaffold.add_argument("--include-claims", action="store_true", help="Allow scaffold apply to create missing claim rows.")
    scaffold.add_argument("--include-evidence", action="store_true", help="Allow scaffold apply to create missing evidence rows and placeholder artifacts.")
    scaffold.set_defaults(func=run_scaffold)

    run = conformance_sub.add_parser(
        "run",
        help="Run conformance cases from registry metadata.",
        description="Resolve selected SSOT conformance case families into governed test rows and execute the stored registry commands.",
    )
    add_path_argument(run)
    run.add_argument("--profiles", nargs="*", default=None, help="Conformance profiles or family names to execute.")
    run.add_argument("--dry-run", action="store_true", help="Resolve governed conformance tests without executing them.")
    run.add_argument("--evidence-output", default=None, help="Optional JSON output path for machine-readable evidence.")
    run.set_defaults(func=run_run)


def run_profile_list(args: argparse.Namespace) -> dict[str, object]:
    from ssot_conformance import list_profiles

    return {"passed": True, "profiles": list_profiles()}


def run_discover(args: argparse.Namespace) -> dict[str, object]:
    from ssot_conformance import discover_cases

    return discover_cases(args.profiles)


def run_scaffold(args: argparse.Namespace) -> dict[str, object]:
    from ssot_conformance import apply_scaffold, plan_scaffold

    if args.apply:
        return apply_scaffold(
            args.path,
            profiles=args.profiles,
            include_claims=args.include_claims,
            include_evidence=args.include_evidence,
        )
    return plan_scaffold(
        args.path,
        profiles=args.profiles,
        include_claims=args.include_claims,
        include_evidence=args.include_evidence,
    )


def run_run(args: argparse.Namespace) -> dict[str, object]:
    from ssot_conformance import build_catalog_slice

    catalog = build_catalog_slice(args.profiles)
    return run_resolved_test_rows(
        args.path,
        target={"kind": "conformance", "profiles": catalog["profiles"], "families": catalog["families"]},
        tests=list(catalog["tests"]),
        evidence_output=args.evidence_output,
        dry_run=args.dry_run,
    )
