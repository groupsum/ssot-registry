from __future__ import annotations

import argparse

from ssot_registry.api import create_entity, delete_entity, get_entity, link_entities, list_entities, run_tests, unlink_entities, update_entity
from ssot_cli.common import add_ids_argument, add_path_argument, collect_list_fields, compact_dict, load_json_object_argument


_LINK_MAPPING = {
    "feature_ids": "feature_ids",
    "claim_ids": "claim_ids",
    "evidence_ids": "evidence_ids",
}


def register_test(subparsers: argparse._SubParsersAction) -> None:
    test = subparsers.add_parser(
        "test",
        help="Test operations.",
        description="Tests are executable or planned verification rows linked to features, claims, and evidence.",
    )
    test_sub = test.add_subparsers(dest="test_command", required=True)

    create = test_sub.add_parser("create", help="Register a verification test.", description="Create a test record and link it to the features, claims, and evidence it exercises.")
    add_path_argument(create)
    create.add_argument("--id", required=True, help="Normalized test id to create.")
    create.add_argument("--title", required=True, help="Human-readable test title.")
    create.add_argument("--status", choices=["planned", "passing", "failing", "blocked", "skipped"], default="planned", help="Current execution or readiness state of the test.")
    create.add_argument("--kind", required=True, help="Operator-defined test category such as unit, integration, or manual.")
    create.add_argument("--test-path", dest="test_path", required=True, help="Repository-relative location of the executable test or test specification.")
    create.add_argument("--feature-ids", nargs="*", default=[], help="Feature ids this test verifies.")
    create.add_argument("--claim-ids", nargs="*", default=[], help="Claim ids this test supports.")
    create.add_argument("--evidence-ids", nargs="*", default=[], help="Evidence ids produced by or associated with the test.")
    create.add_argument("--execution-json", default=None, help="Inline JSON object describing registry-owned execution metadata for this test.")
    create.add_argument("--execution-file", default=None, help="Path to a JSON file containing registry-owned execution metadata for this test.")
    create.set_defaults(func=run_create)

    get = test_sub.add_parser("get", help="Show one test.", description="Fetch a single test record by id.")
    add_path_argument(get)
    get.add_argument("--id", required=True, help="Test id to retrieve.")
    get.set_defaults(func=run_get)

    list_cmd = test_sub.add_parser("list", help="List tests.", description="List test records currently known to the registry.")
    add_path_argument(list_cmd)
    add_ids_argument(list_cmd, help_text="Test ids to include in the list output.")
    list_cmd.set_defaults(func=run_list)

    update = test_sub.add_parser("update", help="Edit test metadata.", description="Update mutable test fields without changing link relationships.")
    add_path_argument(update)
    update.add_argument("--id", required=True, help="Test id to update.")
    update.add_argument("--title", default=None, help="Replacement test title.")
    update.add_argument("--status", choices=["planned", "passing", "failing", "blocked", "skipped"], default=None, help="Updated execution or readiness state.")
    update.add_argument("--kind", default=None, help="Updated test category.")
    update.add_argument("--test-path", dest="test_path", default=None, help="Updated repository-relative path to the test or procedure.")
    update.add_argument("--execution-json", default=None, help="Replacement inline JSON object for test execution metadata.")
    update.add_argument("--execution-file", default=None, help="Replacement JSON file for test execution metadata.")
    update.set_defaults(func=run_update)

    delete = test_sub.add_parser("delete", help="Delete a test.", description="Remove a test record from the registry.")
    add_path_argument(delete)
    delete.add_argument("--id", required=True, help="Test id to delete.")
    delete.set_defaults(func=run_delete)

    link = test_sub.add_parser("link", help="Attach related records to a test.", description="Add links from a test to the features, claims, or evidence it covers.")
    add_path_argument(link)
    link.add_argument("--id", required=True, help="Test id that should receive the links.")
    link.add_argument("--feature-ids", nargs="*", help="Feature ids to attach.")
    link.add_argument("--claim-ids", nargs="*", help="Claim ids to attach.")
    link.add_argument("--evidence-ids", nargs="*", help="Evidence ids to attach.")
    link.set_defaults(func=run_link)

    unlink = test_sub.add_parser("unlink", help="Remove related records from a test.", description="Remove links from a test to features, claims, or evidence.")
    add_path_argument(unlink)
    unlink.add_argument("--id", required=True, help="Test id whose links should be removed.")
    unlink.add_argument("--feature-ids", nargs="*", help="Feature ids to detach.")
    unlink.add_argument("--claim-ids", nargs="*", help="Claim ids to detach.")
    unlink.add_argument("--evidence-ids", nargs="*", help="Evidence ids to detach.")
    unlink.set_defaults(func=run_unlink)

    run = test_sub.add_parser(
        "run",
        help="Execute runnable tests from registry metadata.",
        description="Resolve one or more test rows by id, require execution metadata, and run the stored commands from registry truth.",
    )
    add_path_argument(run)
    selector = run.add_mutually_exclusive_group(required=True)
    selector.add_argument("--id", default=None, help="Single test id to execute.")
    selector.add_argument("--ids", nargs="+", default=None, help="One or more test ids to execute.")
    run.add_argument("--dry-run", action="store_true", help="Resolve tests without executing their commands.")
    run.add_argument("--evidence-output", default=None, help="Optional JSON output path for machine-readable execution evidence.")
    run.set_defaults(func=run_execute)


def _build_links(args: argparse.Namespace) -> dict[str, list[str]]:
    links = collect_list_fields(args, _LINK_MAPPING)
    if not links:
        raise ValueError("At least one link field is required")
    return links


def run_create(args: argparse.Namespace) -> dict[str, object]:
    execution = load_json_object_argument(
        inline_value=args.execution_json,
        file_value=args.execution_file,
        label="test execution metadata",
    )
    row = {
        "id": args.id,
        "title": args.title,
        "status": args.status,
        "kind": args.kind,
        "path": args.test_path,
        "feature_ids": args.feature_ids,
        "claim_ids": args.claim_ids,
        "evidence_ids": args.evidence_ids,
        "execution": execution,
    }
    return create_entity(args.path, "tests", row)


def run_get(args: argparse.Namespace) -> dict[str, object]:
    return get_entity(args.path, "tests", args.id)


def run_list(args: argparse.Namespace) -> dict[str, object]:
    return list_entities(args.path, "tests", ids=args.ids)


def run_update(args: argparse.Namespace) -> dict[str, object]:
    execution = load_json_object_argument(
        inline_value=args.execution_json,
        file_value=args.execution_file,
        label="test execution metadata",
    )
    changes = compact_dict(
        {
            "title": args.title,
            "status": args.status,
            "kind": args.kind,
            "path": args.test_path,
            "execution": execution,
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


def run_execute(args: argparse.Namespace) -> dict[str, object]:
    test_ids = [args.id] if args.id is not None else list(args.ids or [])
    return run_tests(
        args.path,
        test_ids=test_ids,
        evidence_output=args.evidence_output,
        dry_run=args.dry_run,
    )

