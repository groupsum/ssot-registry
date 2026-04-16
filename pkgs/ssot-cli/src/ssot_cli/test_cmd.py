from __future__ import annotations

import argparse

from ssot_registry.api import create_entity, delete_entity, get_entity, link_entities, list_entities, unlink_entities, update_entity
from ssot_cli.common import add_path_argument, collect_list_fields, compact_dict


_LINK_MAPPING = {
    "feature_ids": "feature_ids",
    "claim_ids": "claim_ids",
    "evidence_ids": "evidence_ids",
}


def register_test(subparsers: argparse._SubParsersAction) -> None:
    test = subparsers.add_parser("test", help="Test operations.")
    test_sub = test.add_subparsers(dest="test_command", required=True)

    create = test_sub.add_parser("create", help="Create a test.")
    add_path_argument(create)
    create.add_argument("--id", required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--status", choices=["planned", "passing", "failing", "blocked", "skipped"], default="planned")
    create.add_argument("--kind", required=True)
    create.add_argument("--test-path", dest="test_path", required=True, help="Repository-relative test path.")
    create.add_argument("--feature-ids", nargs="*", default=[])
    create.add_argument("--claim-ids", nargs="*", default=[])
    create.add_argument("--evidence-ids", nargs="*", default=[])
    create.set_defaults(func=run_create)

    get = test_sub.add_parser("get", help="Get one test.")
    add_path_argument(get)
    get.add_argument("--id", required=True)
    get.set_defaults(func=run_get)

    list_cmd = test_sub.add_parser("list", help="List tests.")
    add_path_argument(list_cmd)
    list_cmd.set_defaults(func=run_list)

    update = test_sub.add_parser("update", help="Update test fields.")
    add_path_argument(update)
    update.add_argument("--id", required=True)
    update.add_argument("--title", default=None)
    update.add_argument("--status", choices=["planned", "passing", "failing", "blocked", "skipped"], default=None)
    update.add_argument("--kind", default=None)
    update.add_argument("--test-path", dest="test_path", default=None)
    update.set_defaults(func=run_update)

    delete = test_sub.add_parser("delete", help="Delete a test.")
    add_path_argument(delete)
    delete.add_argument("--id", required=True)
    delete.set_defaults(func=run_delete)

    link = test_sub.add_parser("link", help="Link a test to features, claims, or evidence.")
    add_path_argument(link)
    link.add_argument("--id", required=True)
    link.add_argument("--feature-ids", nargs="*")
    link.add_argument("--claim-ids", nargs="*")
    link.add_argument("--evidence-ids", nargs="*")
    link.set_defaults(func=run_link)

    unlink = test_sub.add_parser("unlink", help="Unlink a test from features, claims, or evidence.")
    add_path_argument(unlink)
    unlink.add_argument("--id", required=True)
    unlink.add_argument("--feature-ids", nargs="*")
    unlink.add_argument("--claim-ids", nargs="*")
    unlink.add_argument("--evidence-ids", nargs="*")
    unlink.set_defaults(func=run_unlink)


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
        "path": args.test_path,
        "feature_ids": args.feature_ids,
        "claim_ids": args.claim_ids,
        "evidence_ids": args.evidence_ids,
    }
    return create_entity(args.path, "tests", row)


def run_get(args: argparse.Namespace) -> dict[str, object]:
    return get_entity(args.path, "tests", args.id)


def run_list(args: argparse.Namespace) -> dict[str, object]:
    return list_entities(args.path, "tests")


def run_update(args: argparse.Namespace) -> dict[str, object]:
    changes = compact_dict(
        {
            "title": args.title,
            "status": args.status,
            "kind": args.kind,
            "path": args.test_path,
        }
    )
    if not changes:
        raise ValueError("At least one update field is required")
    return update_entity(args.path, "tests", args.id, changes)


def run_delete(args: argparse.Namespace) -> dict[str, object]:
    return delete_entity(args.path, "tests", args.id)


def run_link(args: argparse.Namespace) -> dict[str, object]:
    return link_entities(args.path, "tests", args.id, _build_links(args))


def run_unlink(args: argparse.Namespace) -> dict[str, object]:
    return unlink_entities(args.path, "tests", args.id, _build_links(args))

