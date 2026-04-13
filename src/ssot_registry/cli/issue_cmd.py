from __future__ import annotations

import argparse

from ssot_registry.api import plan_issues


def register_issue(subparsers: argparse._SubParsersAction) -> None:
    issue = subparsers.add_parser("issue", help="Issue operations.")
    issue_sub = issue.add_subparsers(dest="issue_command", required=True)

    plan = issue_sub.add_parser("plan", help="Plan issue horizons.")
    plan.add_argument("path", nargs="?", default=".", help="Registry file path or repository root.")
    plan.add_argument("--ids", nargs="+", required=True, help="Issue ids to update.")
    plan.add_argument(
        "--horizon",
        required=True,
        choices=["current", "next", "future", "explicit", "backlog", "out_of_bounds"],
        help="Planning horizon.",
    )
    plan.add_argument("--slot", default=None, help="Explicit slot or label when horizon is explicit.")
    plan.set_defaults(func=run_plan)


def run_plan(args: argparse.Namespace) -> dict[str, object]:
    return plan_issues(path=args.path, ids=args.ids, horizon=args.horizon, slot=args.slot)
