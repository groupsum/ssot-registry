from __future__ import annotations

import argparse

from ssot_registry.api import (
    create_entity,
    delete_entity,
    get_entity,
    link_entities,
    list_entities,
    plan_features,
    set_feature_lifecycle,
    unlink_entities,
    update_entity,
)
from ssot_registry.cli.common import add_optional_bool_argument, add_path_argument, collect_list_fields, compact_dict


_LINK_MAPPING = {
    "claim_ids": "claim_ids",
    "test_ids": "test_ids",
    "requires": "requires",
}


def register_feature(subparsers: argparse._SubParsersAction) -> None:
    feature = subparsers.add_parser("feature", help="Feature operations.")
    feature_sub = feature.add_subparsers(dest="feature_command", required=True)

    create = feature_sub.add_parser("create", help="Create a feature.")
    add_path_argument(create)
    create.add_argument("--id", required=True, help="Feature id.")
    create.add_argument("--title", required=True, help="Feature title.")
    create.add_argument("--description", default="", help="Feature description.")
    create.add_argument("--implementation-status", choices=["absent", "partial", "implemented"], default="absent")
    create.add_argument("--lifecycle-stage", choices=["active", "deprecated", "obsolete", "removed"], default="active")
    create.add_argument("--replacement-feature-id", nargs="*", default=[])
    create.add_argument("--note", default=None)
    create.add_argument("--horizon", choices=["current", "next", "future", "explicit", "backlog", "out_of_bounds"], default="backlog")
    create.add_argument("--claim-tier", choices=["T0", "T1", "T2", "T3", "T4"], default=None)
    create.add_argument("--target-lifecycle-stage", choices=["active", "deprecated", "obsolete", "removed"], default="active")
    create.add_argument("--slot", default=None)
    create.add_argument("--claim-ids", nargs="*", default=[])
    create.add_argument("--test-ids", nargs="*", default=[])
    create.add_argument("--requires", nargs="*", default=[])
    create.set_defaults(func=run_create)

    get = feature_sub.add_parser("get", help="Get one feature.")
    add_path_argument(get)
    get.add_argument("--id", required=True)
    get.set_defaults(func=run_get)

    list_cmd = feature_sub.add_parser("list", help="List features.")
    add_path_argument(list_cmd)
    list_cmd.set_defaults(func=run_list)

    update = feature_sub.add_parser("update", help="Update feature fields.")
    add_path_argument(update)
    update.add_argument("--id", required=True)
    update.add_argument("--title", default=None)
    update.add_argument("--description", default=None)
    update.add_argument("--implementation-status", choices=["absent", "partial", "implemented"], default=None)
    update.set_defaults(func=run_update)

    delete = feature_sub.add_parser("delete", help="Delete a feature.")
    add_path_argument(delete)
    delete.add_argument("--id", required=True)
    delete.set_defaults(func=run_delete)

    link = feature_sub.add_parser("link", help="Link a feature to claims, tests, or required features.")
    add_path_argument(link)
    link.add_argument("--id", required=True)
    link.add_argument("--claim-ids", nargs="*")
    link.add_argument("--test-ids", nargs="*")
    link.add_argument("--requires", nargs="*")
    link.set_defaults(func=run_link)

    unlink = feature_sub.add_parser("unlink", help="Unlink a feature from claims, tests, or required features.")
    add_path_argument(unlink)
    unlink.add_argument("--id", required=True)
    unlink.add_argument("--claim-ids", nargs="*")
    unlink.add_argument("--test-ids", nargs="*")
    unlink.add_argument("--requires", nargs="*")
    unlink.set_defaults(func=run_unlink)

    plan = feature_sub.add_parser("plan", help="Plan feature horizons, tiers, and target lifecycle.")
    add_path_argument(plan)
    plan.add_argument("--ids", nargs="+", required=True, help="Feature ids to update.")
    plan.add_argument(
        "--horizon",
        required=True,
        choices=["current", "next", "future", "explicit", "backlog", "out_of_bounds"],
        help="Planning horizon.",
    )
    plan.add_argument("--claim-tier", choices=["T0", "T1", "T2", "T3", "T4"], default=None, help="Target claim tier.")
    plan.add_argument(
        "--target-lifecycle-stage",
        choices=["active", "deprecated", "obsolete", "removed"],
        default=None,
        help="Planned lifecycle target for the feature.",
    )
    plan.add_argument("--slot", default=None, help="Explicit slot or label when horizon is explicit.")
    plan.set_defaults(func=run_plan)

    lifecycle = feature_sub.add_parser("lifecycle", help="Feature lifecycle operations.")
    lifecycle_sub = lifecycle.add_subparsers(dest="feature_lifecycle_command", required=True)
    lifecycle_set = lifecycle_sub.add_parser("set", help="Set actual feature lifecycle state.")
    add_path_argument(lifecycle_set)
    lifecycle_set.add_argument("--ids", nargs="+", required=True, help="Feature ids to update.")
    lifecycle_set.add_argument("--stage", required=True, choices=["active", "deprecated", "obsolete", "removed"])
    lifecycle_set.add_argument("--replacement-feature-id", nargs="*", default=None, help="Replacement feature id(s).")
    lifecycle_set.add_argument("--effective-release-id", default=None, help="Effective release id.")
    lifecycle_set.add_argument("--note", default=None, help="Lifecycle note or rationale.")
    lifecycle_set.set_defaults(func=run_lifecycle_set)


def _build_links(args: argparse.Namespace) -> dict[str, list[str]]:
    links = collect_list_fields(args, _LINK_MAPPING)
    if not links:
        raise ValueError("At least one link field is required")
    return links


def run_create(args: argparse.Namespace) -> dict[str, object]:
    row = {
        "id": args.id,
        "title": args.title,
        "description": args.description,
        "implementation_status": args.implementation_status,
        "lifecycle": {
            "stage": args.lifecycle_stage,
            "replacement_feature_ids": args.replacement_feature_id,
            "note": args.note,
        },
        "plan": {
            "horizon": args.horizon,
            "slot": args.slot,
            "target_claim_tier": args.claim_tier,
            "target_lifecycle_stage": args.target_lifecycle_stage,
        },
        "claim_ids": args.claim_ids,
        "test_ids": args.test_ids,
        "requires": args.requires,
    }
    return create_entity(args.path, "features", row)


def run_get(args: argparse.Namespace) -> dict[str, object]:
    return get_entity(args.path, "features", args.id)


def run_list(args: argparse.Namespace) -> dict[str, object]:
    return list_entities(args.path, "features")


def run_update(args: argparse.Namespace) -> dict[str, object]:
    changes = compact_dict(
        {
            "title": args.title,
            "description": args.description,
            "implementation_status": args.implementation_status,
        }
    )
    if not changes:
        raise ValueError("At least one update field is required")
    return update_entity(args.path, "features", args.id, changes)


def run_delete(args: argparse.Namespace) -> dict[str, object]:
    return delete_entity(args.path, "features", args.id)


def run_link(args: argparse.Namespace) -> dict[str, object]:
    return link_entities(args.path, "features", args.id, _build_links(args))


def run_unlink(args: argparse.Namespace) -> dict[str, object]:
    return unlink_entities(args.path, "features", args.id, _build_links(args))


def run_plan(args: argparse.Namespace) -> dict[str, object]:
    return plan_features(
        path=args.path,
        ids=args.ids,
        horizon=args.horizon,
        claim_tier=args.claim_tier,
        slot=args.slot,
        target_lifecycle_stage=args.target_lifecycle_stage,
    )


def run_lifecycle_set(args: argparse.Namespace) -> dict[str, object]:
    return set_feature_lifecycle(
        path=args.path,
        ids=args.ids,
        stage=args.stage,
        replacement_feature_ids=args.replacement_feature_id,
        note=args.note,
        effective_release_id=args.effective_release_id,
    )
