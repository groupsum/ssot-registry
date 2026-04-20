from __future__ import annotations

import argparse

from ssot_registry.api import (
    add_boundary_features,
    add_boundary_profiles,
    create_entity,
    delete_entity,
    freeze_boundary,
    get_entity,
    list_entities,
    remove_boundary_features,
    remove_boundary_profiles,
    update_entity,
)
from ssot_cli.common import add_optional_bool_argument, add_path_argument, compact_dict


def register_boundary(subparsers: argparse._SubParsersAction) -> None:
    boundary = subparsers.add_parser(
        "boundary",
        help="Boundary operations.",
        description="Boundaries define the scoped set of direct features and reusable profiles that a release is evaluated against.",
    )
    boundary_sub = boundary.add_subparsers(dest="boundary_command", required=True)

    create = boundary_sub.add_parser("create", help="Define a release boundary.", description="Create a scoped delivery boundary that selects the features and profiles a release is evaluated against.")
    add_path_argument(create)
    create.add_argument("--id", required=True, help="Normalized boundary id to create.")
    create.add_argument("--title", required=True, help="Human-readable boundary title.")
    create.add_argument("--status", choices=["draft", "active", "frozen", "retired"], default="draft", help="Current lifecycle state of the boundary.")
    add_optional_bool_argument(create, "--frozen", default=False, help_text="Record whether the boundary contents are locked against further scope edits.")
    create.add_argument("--feature-ids", nargs="*", default=[], help="Direct feature ids included in the scoped delivery unit.")
    create.add_argument("--profile-ids", nargs="*", default=[], help="Profile ids included in the scoped delivery unit.")
    create.set_defaults(func=run_create)

    get = boundary_sub.add_parser("get", help="Show one boundary.", description="Fetch a single boundary by id.")
    add_path_argument(get)
    get.add_argument("--id", required=True, help="Boundary id to retrieve.")
    get.set_defaults(func=run_get)

    list_cmd = boundary_sub.add_parser("list", help="List boundaries.", description="List boundary records currently known to the registry.")
    add_path_argument(list_cmd)
    list_cmd.set_defaults(func=run_list)

    update = boundary_sub.add_parser("update", help="Edit boundary metadata.", description="Update mutable boundary fields without changing the feature or profile membership lists.")
    add_path_argument(update)
    update.add_argument("--id", required=True, help="Boundary id to update.")
    update.add_argument("--title", default=None, help="Replacement boundary title.")
    update.add_argument("--status", choices=["draft", "active", "frozen", "retired"], default=None, help="Updated lifecycle state.")
    add_optional_bool_argument(update, "--frozen", default=None, help_text="Change whether the boundary is locked against scope edits.")
    update.set_defaults(func=run_update)

    delete = boundary_sub.add_parser("delete", help="Delete a boundary.", description="Remove a boundary record from the registry.")
    add_path_argument(delete)
    delete.add_argument("--id", required=True, help="Boundary id to delete.")
    delete.set_defaults(func=run_delete)

    add_feature = boundary_sub.add_parser("add-feature", help="Add features to a boundary.", description="Include one or more direct features in the scoped delivery boundary.")
    add_path_argument(add_feature)
    add_feature.add_argument("--id", required=True, help="Boundary id that should receive the features.")
    add_feature.add_argument("--feature-ids", nargs="+", required=True, help="Feature ids to include in the boundary.")
    add_feature.set_defaults(func=run_add_feature)

    remove_feature = boundary_sub.add_parser("remove-feature", help="Remove features from a boundary.", description="Remove one or more direct features from the scoped delivery boundary.")
    add_path_argument(remove_feature)
    remove_feature.add_argument("--id", required=True, help="Boundary id whose features should be removed.")
    remove_feature.add_argument("--feature-ids", nargs="+", required=True, help="Feature ids to remove from the boundary.")
    remove_feature.set_defaults(func=run_remove_feature)

    add_profile = boundary_sub.add_parser("add-profile", help="Add profiles to a boundary.", description="Include one or more profiles in the scoped delivery boundary.")
    add_path_argument(add_profile)
    add_profile.add_argument("--id", required=True, help="Boundary id that should receive the profiles.")
    add_profile.add_argument("--profile-ids", nargs="+", required=True, help="Profile ids to include in the boundary.")
    add_profile.set_defaults(func=run_add_profile)

    remove_profile = boundary_sub.add_parser("remove-profile", help="Remove profiles from a boundary.", description="Remove one or more profiles from the scoped delivery boundary.")
    add_path_argument(remove_profile)
    remove_profile.add_argument("--id", required=True, help="Boundary id whose profiles should be removed.")
    remove_profile.add_argument("--profile-ids", nargs="+", required=True, help="Profile ids to remove from the boundary.")
    remove_profile.set_defaults(func=run_remove_profile)

    freeze = boundary_sub.add_parser("freeze", help="Freeze boundary scope.", description="Lock a boundary's resolved scope and emit a snapshot suitable for release workflows.")
    add_path_argument(freeze)
    freeze.add_argument("--boundary-id", default=None, help="Boundary id to freeze. Omit to freeze the active boundary.")
    freeze.set_defaults(func=run_freeze)


def run_create(args: argparse.Namespace) -> dict[str, object]:
    row = {
        "id": args.id,
        "title": args.title,
        "status": args.status,
        "frozen": args.frozen,
        "feature_ids": args.feature_ids,
        "profile_ids": args.profile_ids,
    }
    return create_entity(args.path, "boundaries", row)


def run_get(args: argparse.Namespace) -> dict[str, object]:
    return get_entity(args.path, "boundaries", args.id)


def run_list(args: argparse.Namespace) -> dict[str, object]:
    return list_entities(args.path, "boundaries")


def run_update(args: argparse.Namespace) -> dict[str, object]:
    changes = compact_dict({"title": args.title, "status": args.status, "frozen": args.frozen})
    if not changes:
        raise ValueError("At least one update field is required")
    return update_entity(args.path, "boundaries", args.id, changes)


def run_delete(args: argparse.Namespace) -> dict[str, object]:
    return delete_entity(args.path, "boundaries", args.id)


def run_add_feature(args: argparse.Namespace) -> dict[str, object]:
    return add_boundary_features(args.path, args.id, args.feature_ids)


def run_remove_feature(args: argparse.Namespace) -> dict[str, object]:
    return remove_boundary_features(args.path, args.id, args.feature_ids)


def run_add_profile(args: argparse.Namespace) -> dict[str, object]:
    return add_boundary_profiles(args.path, args.id, args.profile_ids)


def run_remove_profile(args: argparse.Namespace) -> dict[str, object]:
    return remove_boundary_profiles(args.path, args.id, args.profile_ids)


def run_freeze(args: argparse.Namespace) -> dict[str, object]:
    return freeze_boundary(path=args.path, boundary_id=args.boundary_id)

