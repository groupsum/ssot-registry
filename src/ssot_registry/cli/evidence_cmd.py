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
from ssot_registry.cli.common import add_path_argument, collect_list_fields, compact_dict


_LINK_MAPPING = {
    "claim_ids": "claim_ids",
    "test_ids": "test_ids",
}


def register_evidence(subparsers: argparse._SubParsersAction) -> None:
    evidence = subparsers.add_parser("evidence", help="Evidence operations.")
    evidence_sub = evidence.add_subparsers(dest="evidence_command", required=True)

    create = evidence_sub.add_parser("create", help="Create an evidence row.")
    add_path_argument(create)
    create.add_argument("--id", required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--status", choices=["planned", "collected", "passed", "failed", "stale"], default="planned")
    create.add_argument("--kind", required=True)
    create.add_argument("--tier", choices=["T0", "T1", "T2", "T3", "T4"], default="T0")
    create.add_argument("--evidence-path", dest="evidence_path", required=True, help="Repository-relative evidence path.")
    create.add_argument("--claim-ids", nargs="*", default=[])
    create.add_argument("--test-ids", nargs="*", default=[])
    create.set_defaults(func=run_create)

    get = evidence_sub.add_parser("get", help="Get one evidence row.")
    add_path_argument(get)
    get.add_argument("--id", required=True)
    get.set_defaults(func=run_get)

    list_cmd = evidence_sub.add_parser("list", help="List evidence rows.")
    add_path_argument(list_cmd)
    list_cmd.set_defaults(func=run_list)

    update = evidence_sub.add_parser("update", help="Update evidence fields.")
    add_path_argument(update)
    update.add_argument("--id", required=True)
    update.add_argument("--title", default=None)
    update.add_argument("--status", choices=["planned", "collected", "passed", "failed", "stale"], default=None)
    update.add_argument("--kind", default=None)
    update.add_argument("--tier", choices=["T0", "T1", "T2", "T3", "T4"], default=None)
    update.add_argument("--evidence-path", dest="evidence_path", default=None)
    update.set_defaults(func=run_update)

    delete = evidence_sub.add_parser("delete", help="Delete an evidence row.")
    add_path_argument(delete)
    delete.add_argument("--id", required=True)
    delete.set_defaults(func=run_delete)

    link = evidence_sub.add_parser("link", help="Link evidence to claims or tests.")
    add_path_argument(link)
    link.add_argument("--id", required=True)
    link.add_argument("--claim-ids", nargs="*")
    link.add_argument("--test-ids", nargs="*")
    link.set_defaults(func=run_link)

    unlink = evidence_sub.add_parser("unlink", help="Unlink evidence from claims or tests.")
    add_path_argument(unlink)
    unlink.add_argument("--id", required=True)
    unlink.add_argument("--claim-ids", nargs="*")
    unlink.add_argument("--test-ids", nargs="*")
    unlink.set_defaults(func=run_unlink)

    verify = evidence_sub.add_parser("verify", help="Verify one evidence row or all evidence rows.")
    add_path_argument(verify)
    verify.add_argument("--evidence-id", default=None, help="Evidence id to verify. Omit to verify all rows.")
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
