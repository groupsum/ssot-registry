from __future__ import annotations

import argparse
from pathlib import Path

from ssot_registry.api.load import load_registry
from ssot_registry.maturation.selector import build_registry_index, current_verified_tier, next_maturation_slice


def register_maturity(subparsers: argparse._SubParsersAction) -> None:
    maturity = subparsers.add_parser("maturity", help="Inspect claim-tier maturity and next maturation slices.")
    maturity_sub = maturity.add_subparsers(dest="maturity_command", required=True)

    current = maturity_sub.add_parser("current-tier", help="Report the currently verified tier for a feature.")
    current.add_argument("path", nargs="?", default=".")
    current.add_argument("--feature-id", required=True)
    current.set_defaults(func=run_current_tier)

    next_slice = maturity_sub.add_parser("next-slice", help="Preview the next available maturation slice.")
    next_slice.add_argument("path", nargs="?", default=".")
    next_slice.add_argument("--target-tier", default="T2", choices=["T0", "T1", "T2", "T3", "T4"])
    next_slice.set_defaults(func=run_next_slice)


def run_current_tier(args: argparse.Namespace) -> dict[str, object]:
    _registry_path, repo_root, registry = load_registry(Path(args.path))
    index = build_registry_index(registry)
    feature = index["features"].get(args.feature_id)
    if feature is None:
        raise ValueError(f"unknown feature: {args.feature_id}")
    return {
        "passed": True,
        "feature_id": args.feature_id,
        "current_tier": current_verified_tier(registry, feature, repo_root=repo_root),
    }


def run_next_slice(args: argparse.Namespace) -> dict[str, object]:
    _registry_path, repo_root, registry = load_registry(Path(args.path))
    return {
        "passed": True,
        "slice": next_maturation_slice(registry, target_tier=args.target_tier, repo_root=repo_root),
    }
