from __future__ import annotations

import argparse

from ssot_registry.api import (
    create_entity,
    delete_entity,
    get_entity,
    link_entities,
    list_entities,
    plan_issues,
    set_issue_status,
    unlink_entities,
    update_entity,
)
from ssot_cli.common import add_optional_bool_argument, add_path_argument, collect_list_fields, compact_dict


_LINK_MAPPING = {
    "feature_ids": "feature_ids",
    "claim_ids": "claim_ids",
    "test_ids": "test_ids",
    "evidence_ids": "evidence_ids",
    "risk_ids": "risk_ids",
}


def register_issue(subparsers: argparse._SubParsersAction) -> None:
    issue = subparsers.add_parser("issue", help="Issue operations.")
    issue_sub = issue.add_subparsers(dest="issue_command", required=True)

    create = issue_sub.add_parser("create", help="Create an issue.")
    add_path_argument(create)
    create.add_argument("--id", required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--status", choices=["open", "in_progress", "blocked", "resolved", "closed"], default="open")
    create.add_argument("--severity", choices=["low", "medium", "high", "critical"], default="medium")
    create.add_argument("--description", default="")
    create.add_argument("--horizon", choices=["current", "next", "future", "explicit", "backlog", "out_of_bounds"], default="backlog")
    create.add_argument("--slot", default=None)
    create.add_argument("--feature-ids", nargs="*", default=[])
    create.add_argument("--claim-ids", nargs="*", default=[])
    create.add_argument("--test-ids", nargs="*", default=[])
    create.add_argument("--evidence-ids", nargs="*", default=[])
    create.add_argument("--risk-ids", nargs="*", default=[])
    add_optional_bool_argument(create, "--release-blocking", default=False, help_text="Whether the issue blocks release.")
    create.set_defaults(func=run_create)

    get = issue_sub.add_parser("get", help="Get one issue.")
    add_path_argument(get)
    get.add_argument("--id", required=True)
    get.set_defaults(func=run_get)

    list_cmd = issue_sub.add_parser("list", help="List issues.")
    add_path_argument(list_cmd)
    list_cmd.set_defaults(func=run_list)

    update = issue_sub.add_parser("update", help="Update issue fields.")
    add_path_argument(update)
    update.add_argument("--id", required=True)
    update.add_argument("--title", default=None)
    update.add_argument("--severity", choices=["low", "medium", "high", "critical"], default=None)
    update.add_argument("--description", default=None)
    add_optional_bool_argument(update, "--release-blocking", default=None, help_text="Set release blocking state.")
    update.set_defaults(func=run_update)

    delete = issue_sub.add_parser("delete", help="Delete an issue.")
    add_path_argument(delete)
    delete.add_argument("--id", required=True)
    delete.set_defaults(func=run_delete)

    link = issue_sub.add_parser("link", help="Link an issue to related entities.")
    add_path_argument(link)
    link.add_argument("--id", required=True)
    link.add_argument("--feature-ids", nargs="*")
    link.add_argument("--claim-ids", nargs="*")
    link.add_argument("--test-ids", nargs="*")
    link.add_argument("--evidence-ids", nargs="*")
    link.add_argument("--risk-ids", nargs="*")
    link.set_defaults(func=run_link)

    unlink = issue_sub.add_parser("unlink", help="Unlink an issue from related entities.")
    add_path_argument(unlink)
    unlink.add_argument("--id", required=True)
    unlink.add_argument("--feature-ids", nargs="*")
    unlink.add_argument("--claim-ids", nargs="*")
    unlink.add_argument("--test-ids", nargs="*")
    unlink.add_argument("--evidence-ids", nargs="*")
    unlink.add_argument("--risk-ids", nargs="*")
    unlink.set_defaults(func=run_unlink)

    plan = issue_sub.add_parser("plan", help="Plan issue horizons.")
    add_path_argument(plan)
    plan.add_argument("--ids", nargs="+", required=True, help="Issue ids to update.")
    plan.add_argument(
        "--horizon",
        required=True,
        choices=["current", "next", "future", "explicit", "backlog", "out_of_bounds"],
        help="Planning horizon.",
    )
    plan.add_argument("--slot", default=None, help="Explicit slot or label when horizon is explicit.")
    plan.set_defaults(func=run_plan)

    close = issue_sub.add_parser("close", help="Close an issue.")
    add_path_argument(close)
    close.add_argument("--id", required=True)
    close.set_defaults(func=run_close)

    reopen = issue_sub.add_parser("reopen", help="Reopen an issue.")
    add_path_argument(reopen)
    reopen.add_argument("--id", required=True)
    reopen.set_defaults(func=run_reopen)


def _build_links(args: argparse.Namespace) -> dict[str, list[str]]:
    links = collect_list_fields(args, _LINK_MAPPING)
    if not links:
        raise ValueError("At least one link field is required")
    return links


def run_create(args: argparse.Namespace) -> dict[str, object]:
    row = {
        "id": args.id,
        "title": args.title,
        "status": args.status,
        "severity": args.severity,
        "description": args.description,
        "plan": {"horizon": args.horizon, "slot": args.slot},
        "feature_ids": args.feature_ids,
        "claim_ids": args.claim_ids,
        "test_ids": args.test_ids,
        "evidence_ids": args.evidence_ids,
        "risk_ids": args.risk_ids,
        "release_blocking": args.release_blocking,
    }
    return create_entity(args.path, "issues", row)


def run_get(args: argparse.Namespace) -> dict[str, object]:
    return get_entity(args.path, "issues", args.id)


def run_list(args: argparse.Namespace) -> dict[str, object]:
    return list_entities(args.path, "issues")


def run_update(args: argparse.Namespace) -> dict[str, object]:
    changes = compact_dict(
        {
            "title": args.title,
            "severity": args.severity,
            "description": args.description,
            "release_blocking": args.release_blocking,
        }
    )
    if not changes:
        raise ValueError("At least one update field is required")
    return update_entity(args.path, "issues", args.id, changes)


def run_delete(args: argparse.Namespace) -> dict[str, object]:
    return delete_entity(args.path, "issues", args.id)


def run_link(args: argparse.Namespace) -> dict[str, object]:
    return link_entities(args.path, "issues", args.id, _build_links(args))


def run_unlink(args: argparse.Namespace) -> dict[str, object]:
    return unlink_entities(args.path, "issues", args.id, _build_links(args))


def run_plan(args: argparse.Namespace) -> dict[str, object]:
    return plan_issues(path=args.path, ids=args.ids, horizon=args.horizon, slot=args.slot)


def run_close(args: argparse.Namespace) -> dict[str, object]:
    return set_issue_status(args.path, args.id, "closed")


def run_reopen(args: argparse.Namespace) -> dict[str, object]:
    return set_issue_status(args.path, args.id, "open")

