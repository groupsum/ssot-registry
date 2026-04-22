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
from ssot_cli.common import add_ids_argument, add_optional_bool_argument, add_path_argument, collect_list_fields, compact_dict


_LINK_MAPPING = {
    "feature_ids": "feature_ids",
    "claim_ids": "claim_ids",
    "test_ids": "test_ids",
    "evidence_ids": "evidence_ids",
    "issue_ids": "issue_ids",
}


def register_risk(subparsers: argparse._SubParsersAction) -> None:
    risk = subparsers.add_parser(
        "risk",
        help="Risk operations.",
        description="Risks capture active or accepted exposure tied to related features, claims, tests, evidence, and issues.",
    )
    risk_sub = risk.add_subparsers(dest="risk_command", required=True)

    create = risk_sub.add_parser("create", help="Register a new risk.", description="Create a risk record for exposure that must be mitigated, accepted, or tracked through release.")
    add_path_argument(create)
    create.add_argument("--id", required=True, help="Normalized risk id to create.")
    create.add_argument("--title", required=True, help="Human-readable risk title.")
    create.add_argument("--status", choices=["active", "mitigated", "accepted", "retired"], default="active", help="Current treatment state of the risk.")
    create.add_argument("--severity", choices=["low", "medium", "high", "critical"], default="medium", help="Operational severity of the exposure.")
    create.add_argument("--description", default="", help="Operator-facing description of the exposure and context.")
    create.add_argument("--feature-ids", nargs="*", default=[], help="Feature ids exposed by the risk.")
    create.add_argument("--claim-ids", nargs="*", default=[], help="Claim ids affected by the risk.")
    create.add_argument("--test-ids", nargs="*", default=[], help="Test ids related to the risk.")
    create.add_argument("--evidence-ids", nargs="*", default=[], help="Evidence ids related to the risk.")
    create.add_argument("--issue-ids", nargs="*", default=[], help="Issue ids tracking or caused by the risk.")
    add_optional_bool_argument(create, "--release-blocking", default=False, help_text="Mark the risk as a release blocker or explicitly non-blocking.")
    create.set_defaults(func=run_create)

    get = risk_sub.add_parser("get", help="Show one risk.", description="Fetch a single risk record by id.")
    add_path_argument(get)
    get.add_argument("--id", required=True, help="Risk id to retrieve.")
    get.set_defaults(func=run_get)

    list_cmd = risk_sub.add_parser("list", help="List risks.", description="List risk records currently known to the registry.")
    add_path_argument(list_cmd)
    add_ids_argument(list_cmd, help_text="Risk ids to include in the list output.")
    list_cmd.set_defaults(func=run_list)

    update = risk_sub.add_parser("update", help="Edit risk metadata.", description="Update mutable risk fields without changing linked entities.")
    add_path_argument(update)
    update.add_argument("--id", required=True, help="Risk id to update.")
    update.add_argument("--title", default=None, help="Replacement risk title.")
    update.add_argument("--severity", choices=["low", "medium", "high", "critical"], default=None, help="Updated operational severity.")
    update.add_argument("--description", default=None, help="Replacement risk description.")
    add_optional_bool_argument(update, "--release-blocking", default=None, help_text="Change whether the risk is treated as a release blocker.")
    update.set_defaults(func=run_update)

    delete = risk_sub.add_parser("delete", help="Delete a risk.", description="Remove a risk record from the registry.")
    add_path_argument(delete)
    delete.add_argument("--id", required=True, help="Risk id to delete.")
    delete.set_defaults(func=run_delete)

    link = risk_sub.add_parser("link", help="Attach related records to a risk.", description="Add links from a risk to related features, claims, tests, evidence, or issues.")
    add_path_argument(link)
    link.add_argument("--id", required=True, help="Risk id that should receive the links.")
    link.add_argument("--feature-ids", nargs="*", help="Feature ids to attach.")
    link.add_argument("--claim-ids", nargs="*", help="Claim ids to attach.")
    link.add_argument("--test-ids", nargs="*", help="Test ids to attach.")
    link.add_argument("--evidence-ids", nargs="*", help="Evidence ids to attach.")
    link.add_argument("--issue-ids", nargs="*", help="Issue ids to attach.")
    link.set_defaults(func=run_link)

    unlink = risk_sub.add_parser("unlink", help="Remove related records from a risk.", description="Remove links from a risk to features, claims, tests, evidence, or issues.")
    add_path_argument(unlink)
    unlink.add_argument("--id", required=True, help="Risk id whose links should be removed.")
    unlink.add_argument("--feature-ids", nargs="*", help="Feature ids to detach.")
    unlink.add_argument("--claim-ids", nargs="*", help="Claim ids to detach.")
    unlink.add_argument("--test-ids", nargs="*", help="Test ids to detach.")
    unlink.add_argument("--evidence-ids", nargs="*", help="Evidence ids to detach.")
    unlink.add_argument("--issue-ids", nargs="*", help="Issue ids to detach.")
    unlink.set_defaults(func=run_unlink)

    mitigate = risk_sub.add_parser("mitigate", help="Mark a risk mitigated.", description="Set a risk's status to `mitigated`.")
    add_path_argument(mitigate)
    mitigate.add_argument("--id", required=True, help="Risk id to mark mitigated.")
    mitigate.set_defaults(func=run_mitigate)

    accept = risk_sub.add_parser("accept", help="Mark a risk accepted.", description="Set a risk's status to `accepted`.")
    add_path_argument(accept)
    accept.add_argument("--id", required=True, help="Risk id to mark accepted.")
    accept.set_defaults(func=run_accept)

    retire = risk_sub.add_parser("retire", help="Retire a risk.", description="Set a risk's status to `retired`.")
    add_path_argument(retire)
    retire.add_argument("--id", required=True, help="Risk id to retire.")
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
    return list_entities(args.path, "risks", ids=args.ids)


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

