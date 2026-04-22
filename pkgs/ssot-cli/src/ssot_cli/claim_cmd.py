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
from ssot_cli.common import add_ids_argument, add_path_argument, collect_list_fields, compact_dict


_LINK_MAPPING = {
    "feature_ids": "feature_ids",
    "test_ids": "test_ids",
    "evidence_ids": "evidence_ids",
}


def register_claim(subparsers: argparse._SubParsersAction) -> None:
    claim = subparsers.add_parser(
        "claim",
        help="Claim operations.",
        description="Claims are tiered statements about feature behavior that are backed by tests and evidence over time.",
    )
    claim_sub = claim.add_subparsers(dest="claim_command", required=True)

    create = claim_sub.add_parser("create", help="Register a new assurance claim.", description="Create a tiered claim about system behavior and link it to supporting features, tests, and evidence.")
    add_path_argument(create)
    create.add_argument("--id", required=True, help="Normalized claim id to create.")
    create.add_argument("--title", required=True, help="Human-readable claim title.")
    create.add_argument("--status", choices=["proposed", "declared", "implemented", "asserted", "evidenced", "certified", "promoted", "published", "blocked", "retired"], default="proposed", help="Current maturity or publication state of the claim.")
    create.add_argument("--tier", choices=["T0", "T1", "T2", "T3", "T4"], default="T0", help="Assurance tier required for the claim.")
    create.add_argument("--kind", required=True, help="Operator-defined claim category.")
    create.add_argument("--description", default="", help="What the claim asserts and why it matters.")
    create.add_argument("--feature-ids", nargs="*", default=[], help="Feature ids the claim is about.")
    create.add_argument("--test-ids", nargs="*", default=[], help="Test ids that support the claim.")
    create.add_argument("--evidence-ids", nargs="*", default=[], help="Evidence ids that substantiate the claim.")
    create.set_defaults(func=run_create)

    get = claim_sub.add_parser("get", help="Show one claim.", description="Fetch a single claim record by id.")
    add_path_argument(get)
    get.add_argument("--id", required=True, help="Claim id to retrieve.")
    get.set_defaults(func=run_get)

    list_cmd = claim_sub.add_parser("list", help="List claims.", description="List claim records currently known to the registry.")
    add_path_argument(list_cmd)
    add_ids_argument(list_cmd, help_text="Claim ids to include in the list output.")
    list_cmd.set_defaults(func=run_list)

    update = claim_sub.add_parser("update", help="Edit claim metadata.", description="Update mutable claim fields without changing its linked support graph.")
    add_path_argument(update)
    update.add_argument("--id", required=True, help="Claim id to update.")
    update.add_argument("--title", default=None, help="Replacement claim title.")
    update.add_argument("--kind", default=None, help="Updated claim category.")
    update.add_argument("--description", default=None, help="Replacement claim description.")
    update.set_defaults(func=run_update)

    delete = claim_sub.add_parser("delete", help="Delete a claim.", description="Remove a claim record from the registry.")
    add_path_argument(delete)
    delete.add_argument("--id", required=True, help="Claim id to delete.")
    delete.set_defaults(func=run_delete)

    link = claim_sub.add_parser("link", help="Attach related records to a claim.", description="Add links from a claim to the features, tests, or evidence that support it.")
    add_path_argument(link)
    link.add_argument("--id", required=True, help="Claim id that should receive the links.")
    link.add_argument("--feature-ids", nargs="*", help="Feature ids to attach.")
    link.add_argument("--test-ids", nargs="*", help="Test ids to attach.")
    link.add_argument("--evidence-ids", nargs="*", help="Evidence ids to attach.")
    link.set_defaults(func=run_link)

    unlink = claim_sub.add_parser("unlink", help="Remove related records from a claim.", description="Remove links from a claim to features, tests, or evidence.")
    add_path_argument(unlink)
    unlink.add_argument("--id", required=True, help="Claim id whose links should be removed.")
    unlink.add_argument("--feature-ids", nargs="*", help="Feature ids to detach.")
    unlink.add_argument("--test-ids", nargs="*", help="Test ids to detach.")
    unlink.add_argument("--evidence-ids", nargs="*", help="Evidence ids to detach.")
    unlink.set_defaults(func=run_unlink)

    evaluate = claim_sub.add_parser("evaluate", help="Evaluate claim support.", description="Recompute claim support and readiness for one claim or the entire registry.")
    add_path_argument(evaluate)
    evaluate.add_argument("--claim-id", default=None, help="Claim id to evaluate. Omit to evaluate every claim in the registry.")
    evaluate.set_defaults(func=run_evaluate)

    set_status = claim_sub.add_parser("set-status", help="Advance or revise claim status.", description="Change the lifecycle status of a claim without editing other fields.")
    add_path_argument(set_status)
    set_status.add_argument("--id", required=True, help="Claim id whose status should change.")
    set_status.add_argument("--status", required=True, choices=["proposed", "declared", "implemented", "asserted", "evidenced", "certified", "promoted", "published", "blocked", "retired"], help="Target lifecycle or publication state.")
    set_status.set_defaults(func=run_set_status)

    set_tier = claim_sub.add_parser("set-tier", help="Change claim tier.", description="Set the assurance tier expected for a claim.")
    add_path_argument(set_tier)
    set_tier.add_argument("--id", required=True, help="Claim id whose tier should change.")
    set_tier.add_argument("--tier", required=True, choices=["T0", "T1", "T2", "T3", "T4"], help="Target assurance tier to assign.")
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
    return list_entities(args.path, "claims", ids=args.ids)


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

