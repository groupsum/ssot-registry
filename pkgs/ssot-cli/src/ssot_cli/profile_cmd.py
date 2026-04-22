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
from ssot_cli.common import add_ids_argument, add_optional_bool_argument, add_path_argument, collect_list_fields, compact_dict

_LINK_MAPPING = {
    "feature_ids": "feature_ids",
    "profile_ids": "profile_ids",
}


def register_profile(subparsers: argparse._SubParsersAction) -> None:
    profile = subparsers.add_parser(
        "profile",
        help="Profile operations.",
        description="Profiles are reusable bundles of features and nested profiles used for capability, certification, deployment, or interoperability scopes.",
    )
    profile_sub = profile.add_subparsers(dest="profile_command", required=True)

    create = profile_sub.add_parser("create", help="Create a reusable profile.", description="Create a profile that bundles features and nested profiles into an evaluable scope.")
    add_path_argument(create)
    create.add_argument("--id", required=True, help="Normalized profile id to create.")
    create.add_argument("--title", required=True, help="Human-readable profile title.")
    create.add_argument("--description", default="", help="Operator-facing summary of the profile's scope.")
    create.add_argument("--status", choices=["draft", "active", "retired"], default="draft", help="Current lifecycle state of the profile.")
    create.add_argument("--kind", choices=["capability", "certification", "deployment", "interoperability"], default="capability", help="Why the profile exists operationally.")
    create.add_argument("--feature-ids", nargs="*", default=[], help="Feature ids directly included in the profile.")
    create.add_argument("--profile-ids", nargs="*", default=[], help="Nested profile ids included within this profile.")
    create.add_argument("--claim-tier", choices=["T0", "T1", "T2", "T3", "T4"], default=None, help="Default claim tier expected when evaluating the profile.")
    add_optional_bool_argument(
        create,
        "--allow-feature-override-tier",
        default=True,
        help_text="Allow individual features to override the profile-level target claim tier during evaluation.",
    )
    create.set_defaults(func=run_create)

    get = profile_sub.add_parser("get", help="Show one profile.", description="Fetch a single profile by id.")
    add_path_argument(get)
    get.add_argument("--id", required=True, help="Profile id to retrieve.")
    get.set_defaults(func=run_get)

    list_cmd = profile_sub.add_parser("list", help="List profiles.", description="List profile records currently known to the registry.")
    add_path_argument(list_cmd)
    add_ids_argument(list_cmd, help_text="Profile ids to include in the list output.")
    list_cmd.set_defaults(func=run_list)

    update = profile_sub.add_parser("update", help="Edit profile metadata.", description="Update mutable profile fields without changing its link graph.")
    add_path_argument(update)
    update.add_argument("--id", required=True, help="Profile id to update.")
    update.add_argument("--title", default=None, help="Replacement profile title.")
    update.add_argument("--description", default=None, help="Replacement profile description.")
    update.add_argument("--status", choices=["draft", "active", "retired"], default=None, help="New lifecycle state.")
    update.add_argument("--kind", choices=["capability", "certification", "deployment", "interoperability"], default=None, help="New operational role for the profile.")
    update.add_argument("--claim-tier", choices=["T0", "T1", "T2", "T3", "T4"], default=None, help="Updated default claim tier for evaluation.")
    update.set_defaults(func=run_update)

    delete = profile_sub.add_parser("delete", help="Delete a profile.", description="Remove a profile record from the registry.")
    add_path_argument(delete)
    delete.add_argument("--id", required=True, help="Profile id to delete.")
    delete.set_defaults(func=run_delete)

    link = profile_sub.add_parser("link", help="Attach features or nested profiles.", description="Add feature or profile membership to an existing profile.")
    add_path_argument(link)
    link.add_argument("--id", required=True, help="Profile id that should receive the links.")
    link.add_argument("--feature-ids", nargs="*", help="Feature ids to include.")
    link.add_argument("--profile-ids", nargs="*", help="Nested profile ids to include.")
    link.set_defaults(func=run_link)

    unlink = profile_sub.add_parser("unlink", help="Remove features or nested profiles.", description="Remove feature or profile membership from an existing profile.")
    add_path_argument(unlink)
    unlink.add_argument("--id", required=True, help="Profile id whose links should be removed.")
    unlink.add_argument("--feature-ids", nargs="*", help="Feature ids to remove.")
    unlink.add_argument("--profile-ids", nargs="*", help="Nested profile ids to remove.")
    unlink.set_defaults(func=run_unlink)

    evaluate = profile_sub.add_parser("evaluate", help="Evaluate a profile.", description="Resolve the profile and report whether its linked features satisfy the expected claim tier.")
    add_path_argument(evaluate)
    evaluate.add_argument("--profile-id", required=True, help="Profile id to evaluate.")
    evaluate.set_defaults(func=run_evaluate)

    verify = profile_sub.add_parser("verify", help="Verify a profile.", description="Alias for `profile evaluate` for operators who expect verification wording.")
    add_path_argument(verify)
    verify.add_argument("--profile-id", required=True, help="Profile id to verify.")
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
    return list_entities(args.path, "profiles", ids=args.ids)


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

