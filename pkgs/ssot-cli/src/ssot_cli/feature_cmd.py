from __future__ import annotations

import argparse

from ssot_contracts.generated.python.enums import (
    ASSURANCE_ORIGINS,
    CLAIM_TIERS,
    FEATURE_IMPLEMENTATION_STATUSES,
    FEATURE_LIFECYCLE_STAGES,
    OUT_OF_BOUNDS_DISPOSITIONS,
    PLANNING_HORIZONS,
)
from ssot_registry.api import (
    add_feature_children,
    audit_feature_parent_links,
    certify_feature_proof_graphs,
    create_entity,
    create_feature_with_scaffolded_proof_graph,
    delete_entity,
    get_entity,
    link_entities,
    list_feature_children,
    list_entities,
    migrate_feature_parent_audit_edge,
    plan_features,
    resolve_feature_create_auto_scaffold,
    remove_feature_children,
    set_feature_lifecycle,
    set_feature_parents,
    unlink_entities,
    update_entity,
)
from ssot_cli.common import add_ids_argument, add_optional_bool_argument, add_origin_argument, add_path_argument, collect_list_fields, compact_dict, load_text_argument


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
    create.add_argument("--body", default=None, help="Optional longer-form narrative for the feature.")
    create.add_argument("--body-file", default=None, help="Path to a UTF-8 text file containing the feature body.")
    add_origin_argument(create, choices=sorted(ASSURANCE_ORIGINS), default="repo-local")
    create.add_argument("--implementation-status", choices=sorted(FEATURE_IMPLEMENTATION_STATUSES), default="absent", help="Current implementation state in the codebase.")
    create.add_argument("--lifecycle-stage", choices=sorted(FEATURE_LIFECYCLE_STAGES), default="active", help="Actual lifecycle state of the feature today.")
    create.add_argument("--replacement-feature-id", nargs="*", default=[], help="Replacement feature ids if this feature is being deprecated or removed.")
    create.add_argument("--note", default=None, help="Lifecycle note explaining replacement or status context.")
    create.add_argument("--horizon", choices=sorted(PLANNING_HORIZONS), default="backlog", help="Planning horizon that determines when the feature is expected to land.")
    create.add_argument("--out-of-bounds-disposition", choices=sorted(OUT_OF_BOUNDS_DISPOSITIONS), default=None, help="Required when a non-absent feature is out_of_bounds; tolerated means acceptable non-target support, prohibited means removal is required.")
    create.add_argument("--claim-tier", choices=sorted(CLAIM_TIERS), default=None, help="Target assurance tier expected for claims tied to this feature.")
    create.add_argument("--target-lifecycle-stage", choices=sorted(FEATURE_LIFECYCLE_STAGES), default="active", help="Planned future lifecycle target for this feature.")
    create.add_argument("--slot", default=None, help="Explicit planning slot label when the horizon is schedule-driven.")
    create.add_argument("--spec-ids", nargs="*", default=[], help="SPEC ids that define or constrain the feature.")
    create.add_argument("--claim-ids", nargs="*", default=[], help="Claim ids currently attached to the feature.")
    create.add_argument("--test-ids", nargs="*", default=[], help="Test ids that verify the feature.")
    create.add_argument(
        "--requires",
        nargs="*",
        default=[],
        help="Prerequisite feature ids; release and profile gates require them to pass. Not a parent/leaf composition link.",
    )
    create.add_argument("--parent-feature-ids", nargs="*", default=[], help="Inventory parent feature ids; composition only, never a passing prerequisite.")
    add_optional_bool_argument(
        create,
        "--auto-scaffold-proof-graph",
        default=None,
        help_text="Create a minimally valid linked claim, test, and evidence scaffold for this feature in the same transaction.",
    )
    create.set_defaults(func=run_create)

    certify_graph = feature_sub.add_parser(
        "certify-proof-graph",
        help="Execute proof-graph delivery and certification closure for features.",
        description="Run linked tests, materialize source and T3 evidence, add the features to a boundary, create or update a release, certify it, and optionally promote or publish it.",
    )
    add_path_argument(certify_graph)
    certify_graph.add_argument("--ids", nargs="+", required=True, help="Feature ids to drive through proof-graph certification closure.")
    certify_graph.add_argument("--boundary-id", required=True, help="Boundary id to create or update for the selected features.")
    certify_graph.add_argument("--boundary-title", required=True, help="Boundary title to use when creating the boundary.")
    certify_graph.add_argument("--release-id", required=True, help="Release id to create or update for the selected features.")
    certify_graph.add_argument("--release-version", required=True, help="Release version string to record on the release.")
    certify_graph.add_argument(
        "--robustness-dimensions",
        nargs="+",
        required=True,
        help="Robustness dimensions to stamp into the T3 evidence rows.",
    )
    certify_graph.add_argument("--write-report", action="store_true", help="Write the certification report artifact.")
    certify_graph.add_argument("--promote", action="store_true", help="Promote the certified release after certification succeeds.")
    certify_graph.add_argument("--publish", action="store_true", help="Publish the release after certification and promotion succeed.")
    certify_graph.set_defaults(func=run_certify_proof_graph)

    get = feature_sub.add_parser("get", help="Show one feature.", description="Fetch a single feature record by id.")
    add_path_argument(get)
    get.add_argument("--id", required=True, help="Feature id to retrieve.")
    get.set_defaults(func=run_get)

    list_cmd = feature_sub.add_parser("list", help="List features.", description="List feature records currently known to the registry.")
    add_path_argument(list_cmd)
    add_ids_argument(list_cmd, help_text="Feature ids to include in the list output.")
    add_origin_argument(list_cmd, choices=sorted(ASSURANCE_ORIGINS), default=None)
    list_cmd.set_defaults(func=run_list)

    update = feature_sub.add_parser("update", help="Edit feature metadata.", description="Update mutable feature fields without changing links or planning state.")
    add_path_argument(update)
    update.add_argument("--id", required=True, help="Feature id to update.")
    update.add_argument("--title", default=None, help="Replacement feature title.")
    update.add_argument("--description", default=None, help="Replacement feature description.")
    update.add_argument("--body", default=None, help="Replacement longer-form feature narrative.")
    update.add_argument("--body-file", default=None, help="Path to a UTF-8 text file containing the replacement feature body.")
    add_origin_argument(update, choices=sorted(ASSURANCE_ORIGINS), default=None)
    update.add_argument("--implementation-status", choices=sorted(FEATURE_IMPLEMENTATION_STATUSES), default=None, help="Updated implementation state in the codebase.")
    update.set_defaults(func=run_update)

    delete = feature_sub.add_parser("delete", help="Delete a feature.", description="Remove a feature record from the registry.")
    add_path_argument(delete)
    delete.add_argument("--id", required=True, help="Feature id to delete.")
    delete.set_defaults(func=run_delete)

    link = feature_sub.add_parser("link", help="Attach related records to a feature.", description="Add links from a feature to governing SPECs, claims, tests, or prerequisite features enforced by release and profile gates.")
    add_path_argument(link)
    link.add_argument("--id", required=True, help="Feature id that should receive the links.")
    link.add_argument("--spec-ids", nargs="*", help="SPEC ids to attach.")
    link.add_argument("--claim-ids", nargs="*", help="Claim ids to attach.")
    link.add_argument("--test-ids", nargs="*", help="Test ids to attach.")
    link.add_argument(
        "--requires",
        nargs="*",
        help="Prerequisite feature ids to attach; release and profile gates require them to pass. Not parent/leaf composition.",
    )
    link.set_defaults(func=run_link)

    unlink = feature_sub.add_parser("unlink", help="Remove related records from a feature.", description="Remove links from a feature to SPECs, claims, tests, or prerequisite features enforced by release and profile gates.")
    add_path_argument(unlink)
    unlink.add_argument("--id", required=True, help="Feature id whose links should be removed.")
    unlink.add_argument("--spec-ids", nargs="*", help="SPEC ids to detach.")
    unlink.add_argument("--claim-ids", nargs="*", help="Claim ids to detach.")
    unlink.add_argument("--test-ids", nargs="*", help="Test ids to detach.")
    unlink.add_argument("--requires", nargs="*", help="Prerequisite feature ids to detach; release and profile gates require them to pass.")
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
        "--out-of-bounds-disposition",
        choices=sorted(OUT_OF_BOUNDS_DISPOSITIONS),
        default=None,
        help="Disposition for non-absent out_of_bounds features.",
    )
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

    parent = feature_sub.add_parser(
        "parent",
        help="Manage feature parent links.",
        description="Manage inventory composition links only; parent links are never prerequisites or release-readiness gates.",
    )
    parent_sub = parent.add_subparsers(dest="feature_parent_command", required=True)
    for command_name, help_text in (
        ("add", "Add parent links to features."),
        ("set", "Replace parent links on features."),
        ("remove", "Remove parent links from features."),
    ):
        command = parent_sub.add_parser(
            command_name,
            help=help_text,
            description="Mutate inventory composition links only. Use feature link --requires for prerequisites.",
        )
        add_path_argument(command)
        command.add_argument("--ids", nargs="+", required=True, help="Feature ids whose parent links should change.")
        command.add_argument("--parent-ids", nargs="+", required=True, help="Inventory parent feature ids to add, set, or remove; never prerequisites.")
        command.set_defaults(func=run_parent, parent_mode=command_name)
    parent_clear = parent_sub.add_parser("clear", help="Clear all parent links from features.", description="Clear inventory composition links only.")
    add_path_argument(parent_clear)
    parent_clear.add_argument("--ids", nargs="+", required=True, help="Feature ids whose parent links should be cleared.")
    parent_clear.set_defaults(func=run_parent, parent_mode="clear", parent_ids=[])

    children = feature_sub.add_parser("children", help="Manage feature children.", description="Manage derived inventory child links by mutating each child feature's parent_feature_ids field; never prerequisites.")
    children_sub = children.add_subparsers(dest="feature_children_command", required=True)
    children_add = children_sub.add_parser("add", help="Deprecated: add child features to a parent feature.", description="Deprecated convenience mutation for inventory composition only. Use feature parent add for parent links and feature link --requires for prerequisites.")
    add_path_argument(children_add)
    children_add.add_argument("--id", required=True, help="Parent feature id.")
    children_add.add_argument("--child-ids", nargs="+", required=True, help="Deprecated: child feature ids to attach to the inventory parent.")
    children_add.set_defaults(func=run_children_add)

    children_remove = children_sub.add_parser("remove", help="Deprecated: remove child features from a parent feature.", description="Deprecated convenience mutation for inventory composition only. Use feature parent remove for parent links and feature unlink --requires for prerequisites.")
    add_path_argument(children_remove)
    children_remove.add_argument("--id", required=True, help="Parent feature id.")
    children_remove.add_argument("--child-ids", nargs="+", required=True, help="Deprecated: child feature ids to detach from the inventory parent.")
    children_remove.set_defaults(func=run_children_remove)

    children_list = children_sub.add_parser("list", help="List child features for a parent feature.", description="List derived inventory children for a parent feature without mutating the registry.")
    add_path_argument(children_list)
    children_list.add_argument("--id", required=True, help="Parent feature id.")
    children_list.set_defaults(func=run_children_list)

    parent_audit = feature_sub.add_parser(
        "parent-audit",
        help="Audit parent links that may be prerequisite workarounds.",
        description="Report suspicious inventory parent links, or explicitly migrate one parent link into feature.requires.",
    )
    parent_audit.add_argument(
        "path_or_command",
        nargs="?",
        default=".",
        help="Repository path to audit, or the literal 'migrate' to run the opt-in migration helper.",
    )
    parent_audit.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Repository path when using 'migrate'. Defaults to the current directory.",
    )
    parent_audit.add_argument("--feature-id", default=None, help="Feature id whose parent link should be migrated when using 'migrate'.")
    parent_audit.add_argument("--parent-id", default=None, help="Parent feature id to add to requires when using 'migrate'.")
    parent_audit.add_argument("--remove-parent-link", action="store_true", help="When using 'migrate', remove the parent_feature_ids link after adding requires.")
    parent_audit.set_defaults(func=run_parent_audit)


def _build_links(args: argparse.Namespace) -> dict[str, list[str]]:
    links = collect_list_fields(args, _LINK_MAPPING)
    if not links:
        raise ValueError("At least one link field is required")
    return links


def run_create(args: argparse.Namespace) -> dict[str, object]:
    body = load_text_argument(inline_value=args.body, file_value=args.body_file, label="feature")
    plan = {
        "horizon": args.horizon,
        "slot": args.slot,
        "target_claim_tier": args.claim_tier,
        "target_lifecycle_stage": args.target_lifecycle_stage,
    }
    if args.out_of_bounds_disposition is not None:
        plan["out_of_bounds_disposition"] = args.out_of_bounds_disposition

    row = {
        "id": args.id,
        "title": args.title,
        "description": args.description,
        "body": body,
        "origin": args.origin,
        "implementation_status": args.implementation_status,
        "lifecycle": {
            "stage": args.lifecycle_stage,
            "replacement_feature_ids": args.replacement_feature_id,
            "note": args.note,
        },
        "plan": plan,
        "spec_ids": args.spec_ids,
        "claim_ids": args.claim_ids,
        "test_ids": args.test_ids,
        "requires": args.requires,
        "parent_feature_ids": args.parent_feature_ids,
    }
    if resolve_feature_create_auto_scaffold(args.path, args.auto_scaffold_proof_graph):
        return create_feature_with_scaffolded_proof_graph(args.path, row)
    return create_entity(args.path, "features", row)


def run_certify_proof_graph(args: argparse.Namespace) -> dict[str, object]:
    return certify_feature_proof_graphs(
        args.path,
        feature_ids=args.ids,
        boundary_id=args.boundary_id,
        boundary_title=args.boundary_title,
        release_id=args.release_id,
        release_version=args.release_version,
        robustness_dimensions=args.robustness_dimensions,
        write_report=args.write_report,
        promote=args.promote,
        publish=args.publish,
    )


def run_get(args: argparse.Namespace) -> dict[str, object]:
    return get_entity(args.path, "features", args.id)


def run_list(args: argparse.Namespace) -> dict[str, object]:
    return list_entities(args.path, "features", ids=args.ids, origin=args.origin)


def run_update(args: argparse.Namespace) -> dict[str, object]:
    body = load_text_argument(inline_value=args.body, file_value=args.body_file, label="feature")
    changes = compact_dict(
        {
            "title": args.title,
            "description": args.description,
            "body": body,
            "origin": args.origin,
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
        out_of_bounds_disposition=args.out_of_bounds_disposition,
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


def run_parent(args: argparse.Namespace) -> dict[str, object]:
    return set_feature_parents(args.path, args.ids, getattr(args, "parent_ids", []), args.parent_mode)


def run_children_add(args: argparse.Namespace) -> dict[str, object]:
    return add_feature_children(args.path, args.id, args.child_ids)


def run_children_remove(args: argparse.Namespace) -> dict[str, object]:
    return remove_feature_children(args.path, args.id, args.child_ids)


def run_children_list(args: argparse.Namespace) -> list[dict[str, object]]:
    return list_feature_children(args.path, args.id)


def run_parent_audit(args: argparse.Namespace) -> dict[str, object]:
    if args.path_or_command == "migrate":
        if args.feature_id is None or args.parent_id is None:
            raise ValueError("feature parent-audit migrate requires --feature-id and --parent-id")
        return migrate_feature_parent_audit_edge(
            args.path or ".",
            args.feature_id,
            args.parent_id,
            remove_parent_link=args.remove_parent_link,
        )
    if args.path is not None:
        raise ValueError("feature parent-audit accepts either <path> or migrate <path>")
    if args.feature_id is not None or args.parent_id is not None or args.remove_parent_link:
        raise ValueError("feature parent-audit migration flags require the migrate subcommand")
    return audit_feature_parent_links(args.path_or_command)

