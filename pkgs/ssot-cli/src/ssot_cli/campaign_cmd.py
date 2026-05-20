from __future__ import annotations

import argparse
from pathlib import Path

from ssot_registry.control.service import ControlPlane


def register_campaign(subparsers: argparse._SubParsersAction) -> None:
    campaign = subparsers.add_parser("campaign", help="Inspect pull-worker maturation campaign state.")
    campaign_sub = campaign.add_subparsers(dest="campaign_command", required=True)

    status = campaign_sub.add_parser("status", help="Show campaign lease counts and maturity completion.")
    status.add_argument("path", nargs="?", default=".")
    status.add_argument("--campaign-id", required=True)
    status.add_argument("--target-tier", default="T2", choices=["T0", "T1", "T2", "T3", "T4"])
    status.add_argument("--feature-limit", type=int, default=None, help="Override the campaign feature consideration limit.")
    status.set_defaults(func=run_status)


def run_status(args: argparse.Namespace) -> dict[str, object]:
    return ControlPlane(Path(args.path)).get_campaign_status(args.campaign_id, target_tier=args.target_tier, feature_limit=args.feature_limit)
