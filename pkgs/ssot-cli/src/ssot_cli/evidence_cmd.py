from __future__ import annotations

import argparse

from ssot_registry.api import (
    create_entity,
    delete_entity,
    get_entity,
    link_entities,
    list_entities,
    unlink_entities,
    update_entity,
    verify_evidence_rows,
)
from ssot_cli.common import add_path_argument, collect_list_fields, compact_dict


_LINK_MAPPING = {
    "claim_ids": "claim_ids",
    "test_ids": "test_ids",
}


def register_evidence(subparsers: argparse._SubParsersAction) -> None:
    evidence = subparsers.add_parser(
        "evidence",
        help="Evidence operations.",
        description="Evidence rows track artifacts that support claims and test outcomes, such as bundles, logs, or reports.",
    )
    evidence_sub = evidence.add_subparsers(dest="evidence_command", required=True)

    create = evidence_sub.add_parser("create", help="Register a new evidence artifact.", description="Create an evidence row that points at a concrete artifact supporting tests or claims.")
    add_path_argument(create)
    create.add_argument("--id", required=True, help="Normalized evidence id to create.")
    create.add_argument("--title", required=True, help="Human-readable evidence title.")
    create.add_argument("--status", choices=["planned", "collected", "passed", "failed", "stale"], default="planned", help="Current freshness or outcome state of the evidence artifact.")
    create.add_argument("--kind", required=True, help="Operator-defined evidence category such as report, bundle, or log.")
    create.add_argument("--tier", choices=["T0", "T1", "T2", "T3", "T4"], default="T0", help="Assurance tier the evidence contributes toward.")
    create.add_argument("--evidence-path", dest="evidence_path", required=True, help="Repository-relative location of the evidence artifact.")
    create.add_argument("--claim-ids", nargs="*", default=[], help="Claim ids supported by the evidence.")
    create.add_argument("--test-ids", nargs="*", default=[], help="Test ids associated with the evidence.")
    create.set_defaults(func=run_create)

    get = evidence_sub.add_parser("get", help="Show one evidence row.", description="Fetch a single evidence record by id.")
    add_path_argument(get)
    get.add_argument("--id", required=True, help="Evidence id to retrieve.")
    get.set_defaults(func=run_get)

    list_cmd = evidence_sub.add_parser("list", help="List evidence rows.", description="List evidence artifacts currently known to the registry.")
    add_path_argument(list_cmd)
    list_cmd.set_defaults(func=run_list)

    update = evidence_sub.add_parser("update", help="Edit evidence metadata.", description="Update mutable evidence fields without changing its link graph.")
    add_path_argument(update)
    update.add_argument("--id", required=True, help="Evidence id to update.")
    update.add_argument("--title", default=None, help="Replacement evidence title.")
    update.add_argument("--status", choices=["planned", "collected", "passed", "failed", "stale"], default=None, help="Updated freshness or outcome state.")
    update.add_argument("--kind", default=None, help="Updated evidence category.")
    update.add_argument("--tier", choices=["T0", "T1", "T2", "T3", "T4"], default=None, help="Updated assurance tier contribution.")
    update.add_argument("--evidence-path", dest="evidence_path", default=None, help="Updated repository-relative path to the artifact.")
    update.set_defaults(func=run_update)

    delete = evidence_sub.add_parser("delete", help="Delete an evidence row.", description="Remove an evidence record from the registry.")
    add_path_argument(delete)
    delete.add_argument("--id", required=True, help="Evidence id to delete.")
    delete.set_defaults(func=run_delete)

    link = evidence_sub.add_parser("link", help="Attach related claims or tests.", description="Add links from an evidence row to the claims or tests it supports.")
    add_path_argument(link)
    link.add_argument("--id", required=True, help="Evidence id that should receive the links.")
    link.add_argument("--claim-ids", nargs="*", help="Claim ids to attach.")
    link.add_argument("--test-ids", nargs="*", help="Test ids to attach.")
    link.set_defaults(func=run_link)

    unlink = evidence_sub.add_parser("unlink", help="Remove related claims or tests.", description="Remove links from an evidence row to claims or tests.")
    add_path_argument(unlink)
    unlink.add_argument("--id", required=True, help="Evidence id whose links should be removed.")
    unlink.add_argument("--claim-ids", nargs="*", help="Claim ids to detach.")
    unlink.add_argument("--test-ids", nargs="*", help="Test ids to detach.")
    unlink.set_defaults(func=run_unlink)

    verify = evidence_sub.add_parser("verify", help="Verify evidence artifacts.", description="Check one evidence row or all evidence rows for existence and readiness.")
    add_path_argument(verify)
    verify.add_argument("--evidence-id", default=None, help="Evidence id to verify. Omit to verify every evidence row in the registry.")
    verify.set_defaults(func=run_verify)


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
        "kind": args.kind,
        "tier": args.tier,
        "path": args.evidence_path,
        "claim_ids": args.claim_ids,
        "test_ids": args.test_ids,
    }
    return create_entity(args.path, "evidence", row)


def run_get(args: argparse.Namespace) -> dict[str, object]:
    return get_entity(args.path, "evidence", args.id)


def run_list(args: argparse.Namespace) -> dict[str, object]:
    return list_entities(args.path, "evidence")


def run_update(args: argparse.Namespace) -> dict[str, object]:
    changes = compact_dict(
        {
            "title": args.title,
            "status": args.status,
            "kind": args.kind,
            "tier": args.tier,
            "path": args.evidence_path,
        }
    )
    if not changes:
        raise ValueError("At least one update field is required")
    return update_entity(args.path, "evidence", args.id, changes)


def run_delete(args: argparse.Namespace) -> dict[str, object]:
    return delete_entity(args.path, "evidence", args.id)


def run_link(args: argparse.Namespace) -> dict[str, object]:
    return link_entities(args.path, "evidence", args.id, _build_links(args))


def run_unlink(args: argparse.Namespace) -> dict[str, object]:
    return unlink_entities(args.path, "evidence", args.id, _build_links(args))


def run_verify(args: argparse.Namespace) -> dict[str, object]:
    return verify_evidence_rows(path=args.path, evidence_id=args.evidence_id)

