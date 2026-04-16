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
from ssot_registry.cli.common import add_optional_bool_argument, add_path_argument, compact_dict


def register_boundary(subparsers: argparse._SubParsersAction) -> None:
    boundary = subparsers.add_parser("boundary", help="Boundary operations.")
    boundary_sub = boundary.add_subparsers(dest="boundary_command", required=True)

    create = boundary_sub.add_parser("create", help="Create a boundary.")
    add_path_argument(create)
    create.add_argument("--id", required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--status", choices=["draft", "active", "frozen", "retired"], default="draft")
    add_optional_bool_argument(create, "--frozen", default=False, help_text="Whether the boundary is frozen.")
    create.add_argument("--feature-ids", nargs="*", default=[])
    create.add_argument("--profile-ids", nargs="*", default=[])
    create.set_defaults(func=run_create)

    get = boundary_sub.add_parser("get", help="Get one boundary.")
    add_path_argument(get)
    get.add_argument("--id", required=True)
    get.set_defaults(func=run_get)

    list_cmd = boundary_sub.add_parser("list", help="List boundaries.")
    add_path_argument(list_cmd)
    list_cmd.set_defaults(func=run_list)

    update = boundary_sub.add_parser("update", help="Update boundary fields.")
    add_path_argument(update)
    update.add_argument("--id", required=True)
    update.add_argument("--title", default=None)
    update.add_argument("--status", choices=["draft", "active", "frozen", "retired"], default=None)
    add_optional_bool_argument(update, "--frozen", default=None, help_text="Set frozen state.")
    update.set_defaults(func=run_update)

    delete = boundary_sub.add_parser("delete", help="Delete a boundary.")
    add_path_argument(delete)
    delete.add_argument("--id", required=True)
    delete.set_defaults(func=run_delete)

    add_feature = boundary_sub.add_parser("add-feature", help="Add feature ids to a boundary.")
    add_path_argument(add_feature)
    add_feature.add_argument("--id", required=True)
    add_feature.add_argument("--feature-ids", nargs="+", required=True)
    add_feature.set_defaults(func=run_add_feature)

    remove_feature = boundary_sub.add_parser("remove-feature", help="Remove feature ids from a boundary.")
    add_path_argument(remove_feature)
    remove_feature.add_argument("--id", required=True)
    remove_feature.add_argument("--feature-ids", nargs="+", required=True)
    remove_feature.set_defaults(func=run_remove_feature)

    add_profile = boundary_sub.add_parser("add-profile", help="Add profile ids to a boundary.")
    add_path_argument(add_profile)
    add_profile.add_argument("--id", required=True)
    add_profile.add_argument("--profile-ids", nargs="+", required=True)
    add_profile.set_defaults(func=run_add_profile)

    remove_profile = boundary_sub.add_parser("remove-profile", help="Remove profile ids from a boundary.")
    add_path_argument(remove_profile)
    remove_profile.add_argument("--id", required=True)
    remove_profile.add_argument("--profile-ids", nargs="+", required=True)
    remove_profile.set_defaults(func=run_remove_profile)

    freeze = boundary_sub.add_parser("freeze", help="Freeze a boundary and emit a snapshot.")
    add_path_argument(freeze)
    freeze.add_argument("--boundary-id", default=None, help="Boundary id. Defaults to the active boundary.")
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
