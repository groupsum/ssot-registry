from __future__ import annotations

import argparse

from ssot_registry.api import (
    create_entity,
    delete_entity,
    get_entity,
    link_entities,
    list_entities,
    set_risk_status,
    unlink_entities,
    update_entity,
)
from ssot_cli.common import add_optional_bool_argument, add_path_argument, collect_list_fields, compact_dict


_LINK_MAPPING = {
    "feature_ids": "feature_ids",
    "claim_ids": "claim_ids",
    "test_ids": "test_ids",
    "evidence_ids": "evidence_ids",
    "issue_ids": "issue_ids",
}


def register_risk(subparsers: argparse._SubParsersAction) -> None:
    risk = subparsers.add_parser("risk", help="Risk operations.")
    risk_sub = risk.add_subparsers(dest="risk_command", required=True)

    create = risk_sub.add_parser("create", help="Create a risk.")
    add_path_argument(create)
    create.add_argument("--id", required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--status", choices=["active", "mitigated", "accepted", "retired"], default="active")
    create.add_argument("--severity", choices=["low", "medium", "high", "critical"], default="medium")
    create.add_argument("--description", default="")
    create.add_argument("--feature-ids", nargs="*", default=[])
    create.add_argument("--claim-ids", nargs="*", default=[])
    create.add_argument("--test-ids", nargs="*", default=[])
    create.add_argument("--evidence-ids", nargs="*", default=[])
    create.add_argument("--issue-ids", nargs="*", default=[])
    add_optional_bool_argument(create, "--release-blocking", default=False, help_text="Whether the risk blocks release.")
    create.set_defaults(func=run_create)

    get = risk_sub.add_parser("get", help="Get one risk.")
    add_path_argument(get)
    get.add_argument("--id", required=True)
    get.set_defaults(func=run_get)

    list_cmd = risk_sub.add_parser("list", help="List risks.")
    add_path_argument(list_cmd)
    list_cmd.set_defaults(func=run_list)

    update = risk_sub.add_parser("update", help="Update risk fields.")
    add_path_argument(update)
    update.add_argument("--id", required=True)
    update.add_argument("--title", default=None)
    update.add_argument("--severity", choices=["low", "medium", "high", "critical"], default=None)
    update.add_argument("--description", default=None)
    add_optional_bool_argument(update, "--release-blocking", default=None, help_text="Set release blocking state.")
    update.set_defaults(func=run_update)

    delete = risk_sub.add_parser("delete", help="Delete a risk.")
    add_path_argument(delete)
    delete.add_argument("--id", required=True)
    delete.set_defaults(func=run_delete)

    link = risk_sub.add_parser("link", help="Link a risk to related entities.")
    add_path_argument(link)
    link.add_argument("--id", required=True)
    link.add_argument("--feature-ids", nargs="*")
    link.add_argument("--claim-ids", nargs="*")
    link.add_argument("--test-ids", nargs="*")
    link.add_argument("--evidence-ids", nargs="*")
    link.add_argument("--issue-ids", nargs="*")
    link.set_defaults(func=run_link)

    unlink = risk_sub.add_parser("unlink", help="Unlink a risk from related entities.")
    add_path_argument(unlink)
    unlink.add_argument("--id", required=True)
    unlink.add_argument("--feature-ids", nargs="*")
    unlink.add_argument("--claim-ids", nargs="*")
    unlink.add_argument("--test-ids", nargs="*")
    unlink.add_argument("--evidence-ids", nargs="*")
    unlink.add_argument("--issue-ids", nargs="*")
    unlink.set_defaults(func=run_unlink)

    mitigate = risk_sub.add_parser("mitigate", help="Mark a risk mitigated.")
    add_path_argument(mitigate)
    mitigate.add_argument("--id", required=True)
    mitigate.set_defaults(func=run_mitigate)

    accept = risk_sub.add_parser("accept", help="Mark a risk accepted.")
    add_path_argument(accept)
    accept.add_argument("--id", required=True)
    accept.set_defaults(func=run_accept)

    retire = risk_sub.add_parser("retire", help="Retire a risk.")
    add_path_argument(retire)
    retire.add_argument("--id", required=True)
    retire.set_defaults(func=run_retire)


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
        "feature_ids": args.feature_ids,
        "claim_ids": args.claim_ids,
        "test_ids": args.test_ids,
        "evidence_ids": args.evidence_ids,
        "issue_ids": args.issue_ids,
        "release_blocking": args.release_blocking,
    }
    return create_entity(args.path, "risks", row)


def run_get(args: argparse.Namespace) -> dict[str, object]:
    return get_entity(args.path, "risks", args.id)


def run_list(args: argparse.Namespace) -> dict[str, object]:
    return list_entities(args.path, "risks")


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
    return update_entity(args.path, "risks", args.id, changes)


def run_delete(args: argparse.Namespace) -> dict[str, object]:
    return delete_entity(args.path, "risks", args.id)


def run_link(args: argparse.Namespace) -> dict[str, object]:
    return link_entities(args.path, "risks", args.id, _build_links(args))


def run_unlink(args: argparse.Namespace) -> dict[str, object]:
    return unlink_entities(args.path, "risks", args.id, _build_links(args))


def run_mitigate(args: argparse.Namespace) -> dict[str, object]:
    return set_risk_status(args.path, args.id, "mitigated")


def run_accept(args: argparse.Namespace) -> dict[str, object]:
    return set_risk_status(args.path, args.id, "accepted")


def run_retire(args: argparse.Namespace) -> dict[str, object]:
    return set_risk_status(args.path, args.id, "retired")

