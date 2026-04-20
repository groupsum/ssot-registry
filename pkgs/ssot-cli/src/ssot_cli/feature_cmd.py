from __future__ import annotations

import argparse

from ssot_contracts.generated.python.enums import CLAIM_TIERS, FEATURE_IMPLEMENTATION_STATUSES, FEATURE_LIFECYCLE_STAGES, PLANNING_HORIZONS
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
from ssot_cli.common import add_optional_bool_argument, add_path_argument, collect_list_fields, compact_dict


_LINK_MAPPING = {
    "spec_ids": "spec_ids",
    "claim_ids": "claim_ids",
    "test_ids": "test_ids",
    "requires": "requires",
}


def register_feature(subparsers: argparse._SubParsersAction) -> None:
    feature = subparsers.add_parser(
        "feature",
        help="Feature operations.",
        description="Features are targetable implementation units that connect planning, claims, tests, and supporting specs.",
    )
    feature_sub = feature.add_subparsers(dest="feature_command", required=True)

    create = feature_sub.add_parser(
        "create",
        help="Register a new implementation feature.",
        description="Create a feature record that links planned delivery, implementation state, and verification artifacts.",
    )
    add_path_argument(create)
    create.add_argument("--id", required=True, help="Normalized feature id to create.")
    create.add_argument("--title", required=True, help="Human-readable feature title.")
    create.add_argument("--description", default="", help="Operator-facing summary of the feature's purpose.")
    create.add_argument("--implementation-status", choices=sorted(FEATURE_IMPLEMENTATION_STATUSES), default="absent", help="Current implementation state in the codebase.")
    create.add_argument("--lifecycle-stage", choices=sorted(FEATURE_LIFECYCLE_STAGES), default="active", help="Actual lifecycle state of the feature today.")
    create.add_argument("--replacement-feature-id", nargs="*", default=[], help="Replacement feature ids if this feature is being deprecated or removed.")
    create.add_argument("--note", default=None, help="Lifecycle note explaining replacement or status context.")
    create.add_argument("--horizon", choices=sorted(PLANNING_HORIZONS), default="backlog", help="Planning horizon that determines when the feature is expected to land.")
    create.add_argument("--claim-tier", choices=sorted(CLAIM_TIERS), default=None, help="Target assurance tier expected for claims tied to this feature.")
    create.add_argument("--target-lifecycle-stage", choices=sorted(FEATURE_LIFECYCLE_STAGES), default="active", help="Planned future lifecycle target for this feature.")
    create.add_argument("--slot", default=None, help="Explicit planning slot label when the horizon is schedule-driven.")
    create.add_argument("--spec-ids", nargs="*", default=[], help="SPEC ids that define or constrain the feature.")
    create.add_argument("--claim-ids", nargs="*", default=[], help="Claim ids currently attached to the feature.")
    create.add_argument("--test-ids", nargs="*", default=[], help="Test ids that verify the feature.")
    create.add_argument("--requires", nargs="*", default=[], help="Other feature ids that this feature depends on.")
    create.set_defaults(func=run_create)

    get = feature_sub.add_parser("get", help="Show one feature.", description="Fetch a single feature record by id.")
    add_path_argument(get)
    get.add_argument("--id", required=True, help="Feature id to retrieve.")
    get.set_defaults(func=run_get)

    list_cmd = feature_sub.add_parser("list", help="List features.", description="List feature records currently known to the registry.")
    add_path_argument(list_cmd)
    list_cmd.set_defaults(func=run_list)

    update = feature_sub.add_parser("update", help="Edit feature metadata.", description="Update mutable feature fields without changing links or planning state.")
    add_path_argument(update)
    update.add_argument("--id", required=True, help="Feature id to update.")
    update.add_argument("--title", default=None, help="Replacement feature title.")
    update.add_argument("--description", default=None, help="Replacement feature description.")
    update.add_argument("--implementation-status", choices=sorted(FEATURE_IMPLEMENTATION_STATUSES), default=None, help="Updated implementation state in the codebase.")
    update.set_defaults(func=run_update)

    delete = feature_sub.add_parser("delete", help="Delete a feature.", description="Remove a feature record from the registry.")
    add_path_argument(delete)
    delete.add_argument("--id", required=True, help="Feature id to delete.")
    delete.set_defaults(func=run_delete)

    link = feature_sub.add_parser("link", help="Attach related records to a feature.", description="Add links from a feature to governing SPECs, claims, tests, or prerequisite features.")
    add_path_argument(link)
    link.add_argument("--id", required=True, help="Feature id that should receive the links.")
    link.add_argument("--spec-ids", nargs="*", help="SPEC ids to attach.")
    link.add_argument("--claim-ids", nargs="*", help="Claim ids to attach.")
    link.add_argument("--test-ids", nargs="*", help="Test ids to attach.")
    link.add_argument("--requires", nargs="*", help="Dependency feature ids to attach.")
    link.set_defaults(func=run_link)

    unlink = feature_sub.add_parser("unlink", help="Remove related records from a feature.", description="Remove links from a feature to SPECs, claims, tests, or prerequisite features.")
    add_path_argument(unlink)
    unlink.add_argument("--id", required=True, help="Feature id whose links should be removed.")
    unlink.add_argument("--spec-ids", nargs="*", help="SPEC ids to detach.")
    unlink.add_argument("--claim-ids", nargs="*", help="Claim ids to detach.")
    unlink.add_argument("--test-ids", nargs="*", help="Test ids to detach.")
    unlink.add_argument("--requires", nargs="*", help="Dependency feature ids to detach.")
    unlink.set_defaults(func=run_unlink)

    plan = feature_sub.add_parser("plan", help="Set planned rollout targets.", description="Update feature planning fields such as horizon, target claim tier, and future lifecycle.")
    add_path_argument(plan)
    plan.add_argument("--ids", nargs="+", required=True, help="Feature ids whose planning fields should change.")
    plan.add_argument(
        "--horizon",
        required=True,
        choices=sorted(PLANNING_HORIZONS),
        help="Planning horizon to assign.",
    )
    plan.add_argument("--claim-tier", choices=sorted(CLAIM_TIERS), default=None, help="Target claim tier for the selected features.")
    plan.add_argument(
        "--target-lifecycle-stage",
        choices=sorted(FEATURE_LIFECYCLE_STAGES),
        default=None,
        help="Future lifecycle stage the selected features are expected to move toward.",
    )
    plan.add_argument("--slot", default=None, help="Explicit release train, sprint, or slot label for `explicit` horizons.")
    plan.set_defaults(func=run_plan)

    lifecycle = feature_sub.add_parser("lifecycle", help="Manage actual lifecycle state.", description="Set the current lifecycle state for one or more features.")
    lifecycle_sub = lifecycle.add_subparsers(dest="feature_lifecycle_command", required=True)
    lifecycle_set = lifecycle_sub.add_parser("set", help="Set current lifecycle state.", description="Record the actual lifecycle state for one or more features.")
    add_path_argument(lifecycle_set)
    lifecycle_set.add_argument("--ids", nargs="+", required=True, help="Feature ids whose current lifecycle should change.")
    lifecycle_set.add_argument("--stage", required=True, choices=sorted(FEATURE_LIFECYCLE_STAGES), help="Current lifecycle stage to record.")
    lifecycle_set.add_argument("--replacement-feature-id", nargs="*", default=None, help="Replacement feature ids to record for deprecated or removed features.")
    lifecycle_set.add_argument("--effective-release-id", default=None, help="Release id when the lifecycle change takes effect.")
    lifecycle_set.add_argument("--note", default=None, help="Lifecycle rationale or operator note.")
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
        "spec_ids": args.spec_ids,
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

