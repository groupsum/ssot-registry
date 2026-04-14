from __future__ import annotations

import argparse

from ssot_registry.api import (
    create_entity,
    delete_entity,
    evaluate_claims,
    get_entity,
    link_entities,
    list_entities,
    set_claim_status,
    set_claim_tier,
    unlink_entities,
    update_entity,
)
from ssot_registry.cli.common import add_path_argument, collect_list_fields, compact_dict


_LINK_MAPPING = {
    "feature_ids": "feature_ids",
    "test_ids": "test_ids",
    "evidence_ids": "evidence_ids",
}


def register_claim(subparsers: argparse._SubParsersAction) -> None:
    claim = subparsers.add_parser("claim", help="Claim operations.")
    claim_sub = claim.add_subparsers(dest="claim_command", required=True)

    create = claim_sub.add_parser("create", help="Create a claim.")
    add_path_argument(create)
    create.add_argument("--id", required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--status", choices=["proposed", "declared", "implemented", "asserted", "evidenced", "certified", "promoted", "published", "blocked", "retired"], default="proposed")
    create.add_argument("--tier", choices=["T0", "T1", "T2", "T3", "T4"], default="T0")
    create.add_argument("--kind", required=True)
    create.add_argument("--description", default="")
    create.add_argument("--feature-ids", nargs="*", default=[])
    create.add_argument("--test-ids", nargs="*", default=[])
    create.add_argument("--evidence-ids", nargs="*", default=[])
    create.set_defaults(func=run_create)

    get = claim_sub.add_parser("get", help="Get one claim.")
    add_path_argument(get)
    get.add_argument("--id", required=True)
    get.set_defaults(func=run_get)

    list_cmd = claim_sub.add_parser("list", help="List claims.")
    add_path_argument(list_cmd)
    list_cmd.set_defaults(func=run_list)

    update = claim_sub.add_parser("update", help="Update claim fields.")
    add_path_argument(update)
    update.add_argument("--id", required=True)
    update.add_argument("--title", default=None)
    update.add_argument("--kind", default=None)
    update.add_argument("--description", default=None)
    update.set_defaults(func=run_update)

    delete = claim_sub.add_parser("delete", help="Delete a claim.")
    add_path_argument(delete)
    delete.add_argument("--id", required=True)
    delete.set_defaults(func=run_delete)

    link = claim_sub.add_parser("link", help="Link a claim to features, tests, or evidence.")
    add_path_argument(link)
    link.add_argument("--id", required=True)
    link.add_argument("--feature-ids", nargs="*")
    link.add_argument("--test-ids", nargs="*")
    link.add_argument("--evidence-ids", nargs="*")
    link.set_defaults(func=run_link)

    unlink = claim_sub.add_parser("unlink", help="Unlink a claim from features, tests, or evidence.")
    add_path_argument(unlink)
    unlink.add_argument("--id", required=True)
    unlink.add_argument("--feature-ids", nargs="*")
    unlink.add_argument("--test-ids", nargs="*")
    unlink.add_argument("--evidence-ids", nargs="*")
    unlink.set_defaults(func=run_unlink)

    evaluate = claim_sub.add_parser("evaluate", help="Evaluate one claim or all claims.")
    add_path_argument(evaluate)
    evaluate.add_argument("--claim-id", default=None, help="Claim id to evaluate. Omit to evaluate all claims.")
    evaluate.set_defaults(func=run_evaluate)

    set_status = claim_sub.add_parser("set-status", help="Set claim status.")
    add_path_argument(set_status)
    set_status.add_argument("--id", required=True)
    set_status.add_argument("--status", required=True, choices=["proposed", "declared", "implemented", "asserted", "evidenced", "certified", "promoted", "published", "blocked", "retired"])
    set_status.set_defaults(func=run_set_status)

    set_tier = claim_sub.add_parser("set-tier", help="Set claim tier.")
    add_path_argument(set_tier)
    set_tier.add_argument("--id", required=True)
    set_tier.add_argument("--tier", required=True, choices=["T0", "T1", "T2", "T3", "T4"])
    set_tier.set_defaults(func=run_set_tier)


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
        "tier": args.tier,
        "kind": args.kind,
        "description": args.description,
        "feature_ids": args.feature_ids,
        "test_ids": args.test_ids,
        "evidence_ids": args.evidence_ids,
    }
    return create_entity(args.path, "claims", row)


def run_get(args: argparse.Namespace) -> dict[str, object]:
    return get_entity(args.path, "claims", args.id)


def run_list(args: argparse.Namespace) -> dict[str, object]:
    return list_entities(args.path, "claims")


def run_update(args: argparse.Namespace) -> dict[str, object]:
    changes = compact_dict({"title": args.title, "kind": args.kind, "description": args.description})
    if not changes:
        raise ValueError("At least one update field is required")
    return update_entity(args.path, "claims", args.id, changes)


def run_delete(args: argparse.Namespace) -> dict[str, object]:
    return delete_entity(args.path, "claims", args.id)


def run_link(args: argparse.Namespace) -> dict[str, object]:
    return link_entities(args.path, "claims", args.id, _build_links(args))


def run_unlink(args: argparse.Namespace) -> dict[str, object]:
    return unlink_entities(args.path, "claims", args.id, _build_links(args))


def run_evaluate(args: argparse.Namespace) -> dict[str, object]:
    return evaluate_claims(path=args.path, claim_id=args.claim_id)


def run_set_status(args: argparse.Namespace) -> dict[str, object]:
    return set_claim_status(args.path, args.id, args.status)


def run_set_tier(args: argparse.Namespace) -> dict[str, object]:
    return set_claim_tier(args.path, args.id, args.tier)
