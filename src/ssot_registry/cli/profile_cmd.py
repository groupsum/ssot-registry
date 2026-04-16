from __future__ import annotations

import argparse

from ssot_registry.api import (
    create_entity,
    delete_entity,
    evaluate_profile_by_id,
    get_entity,
    link_entities,
    list_entities,
    unlink_entities,
    update_entity,
)
from ssot_registry.cli.common import add_optional_bool_argument, add_path_argument, collect_list_fields, compact_dict

_LINK_MAPPING = {
    "feature_ids": "feature_ids",
    "profile_ids": "profile_ids",
}


def register_profile(subparsers: argparse._SubParsersAction) -> None:
    profile = subparsers.add_parser("profile", help="Profile operations.")
    profile_sub = profile.add_subparsers(dest="profile_command", required=True)

    create = profile_sub.add_parser("create", help="Create a profile.")
    add_path_argument(create)
    create.add_argument("--id", required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--description", default="")
    create.add_argument("--status", choices=["draft", "active", "retired"], default="draft")
    create.add_argument("--kind", choices=["capability", "certification", "deployment", "interoperability"], default="capability")
    create.add_argument("--feature-ids", nargs="*", default=[])
    create.add_argument("--profile-ids", nargs="*", default=[])
    create.add_argument("--claim-tier", choices=["T0", "T1", "T2", "T3", "T4"], default=None)
    add_optional_bool_argument(
        create,
        "--allow-feature-override-tier",
        default=True,
        help_text="Allow feature-level target tier override.",
    )
    create.set_defaults(func=run_create)

    get = profile_sub.add_parser("get", help="Get one profile.")
    add_path_argument(get)
    get.add_argument("--id", required=True)
    get.set_defaults(func=run_get)

    list_cmd = profile_sub.add_parser("list", help="List profiles.")
    add_path_argument(list_cmd)
    list_cmd.set_defaults(func=run_list)

    update = profile_sub.add_parser("update", help="Update profile fields.")
    add_path_argument(update)
    update.add_argument("--id", required=True)
    update.add_argument("--title", default=None)
    update.add_argument("--description", default=None)
    update.add_argument("--status", choices=["draft", "active", "retired"], default=None)
    update.add_argument("--kind", choices=["capability", "certification", "deployment", "interoperability"], default=None)
    update.add_argument("--claim-tier", choices=["T0", "T1", "T2", "T3", "T4"], default=None)
    update.set_defaults(func=run_update)

    delete = profile_sub.add_parser("delete", help="Delete a profile.")
    add_path_argument(delete)
    delete.add_argument("--id", required=True)
    delete.set_defaults(func=run_delete)

    link = profile_sub.add_parser("link", help="Link a profile to features or nested profiles.")
    add_path_argument(link)
    link.add_argument("--id", required=True)
    link.add_argument("--feature-ids", nargs="*")
    link.add_argument("--profile-ids", nargs="*")
    link.set_defaults(func=run_link)

    unlink = profile_sub.add_parser("unlink", help="Unlink a profile from features or nested profiles.")
    add_path_argument(unlink)
    unlink.add_argument("--id", required=True)
    unlink.add_argument("--feature-ids", nargs="*")
    unlink.add_argument("--profile-ids", nargs="*")
    unlink.set_defaults(func=run_unlink)

    evaluate = profile_sub.add_parser("evaluate", help="Evaluate a profile.")
    add_path_argument(evaluate)
    evaluate.add_argument("--profile-id", required=True)
    evaluate.set_defaults(func=run_evaluate)

    verify = profile_sub.add_parser("verify", help="Alias for profile evaluate.")
    add_path_argument(verify)
    verify.add_argument("--profile-id", required=True)
    verify.set_defaults(func=run_evaluate)


def _build_links(args: argparse.Namespace) -> dict[str, list[str]]:
    links = collect_list_fields(args, _LINK_MAPPING)
    if not links:
        raise ValueError("At least one link field is required")
    return links


def run_create(args: argparse.Namespace) -> dict[str, object]:
    return create_entity(
        args.path,
        "profiles",
        {
            "id": args.id,
            "title": args.title,
            "description": args.description,
            "status": args.status,
            "kind": args.kind,
            "feature_ids": args.feature_ids,
            "profile_ids": args.profile_ids,
            "claim_tier": args.claim_tier,
            "evaluation": {
                "mode": "all_features_must_pass",
                "allow_feature_override_tier": args.allow_feature_override_tier,
            },
        },
    )


def run_get(args: argparse.Namespace) -> dict[str, object]:
    return get_entity(args.path, "profiles", args.id)


def run_list(args: argparse.Namespace) -> dict[str, object]:
    return list_entities(args.path, "profiles")


def run_update(args: argparse.Namespace) -> dict[str, object]:
    changes = compact_dict(
        {
            "title": args.title,
            "description": args.description,
            "status": args.status,
            "kind": args.kind,
            "claim_tier": args.claim_tier,
        }
    )
    if not changes:
        raise ValueError("At least one update field is required")
    return update_entity(args.path, "profiles", args.id, changes)


def run_delete(args: argparse.Namespace) -> dict[str, object]:
    return delete_entity(args.path, "profiles", args.id)


def run_link(args: argparse.Namespace) -> dict[str, object]:
    return link_entities(args.path, "profiles", args.id, _build_links(args))


def run_unlink(args: argparse.Namespace) -> dict[str, object]:
    return unlink_entities(args.path, "profiles", args.id, _build_links(args))


def run_evaluate(args: argparse.Namespace) -> dict[str, object]:
    return evaluate_profile_by_id(args.path, args.profile_id)
