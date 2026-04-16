from __future__ import annotations

import argparse

from ssot_registry.api import (
    create_document,
    create_document_reservation,
    delete_document,
    get_document,
    list_document_reservations,
    list_documents,
    set_document_status,
    sync_documents,
    supersede_documents,
    update_document,
)
from ssot_registry.cli.common import add_path_argument, compact_dict


def register_spec(subparsers: argparse._SubParsersAction) -> None:
    spec = subparsers.add_parser("spec", help="Spec operations.")
    spec_sub = spec.add_subparsers(dest="spec_command", required=True)

    create = spec_sub.add_parser("create", help="Create a repo-local spec.")
    add_path_argument(create)
    create.add_argument("--title", required=True)
    create.add_argument("--slug", required=True)
    create.add_argument("--body-file", required=True)
    create.add_argument("--number", type=int, default=None)
    create.add_argument("--origin", choices=["repo-local"], default="repo-local")
    create.add_argument("--kind", choices=["normative", "operational", "repo-local"], default="repo-local")
    create.add_argument("--status", choices=["draft", "in_review", "accepted", "rejected", "withdrawn", "superseded", "retired"], default="draft")
    create.add_argument("--note", default=None, help="Optional lifecycle note.")
    create.add_argument("--reserve-range", default=None, help="Reservation owner to allocate from.")
    create.set_defaults(func=run_create)

    get = spec_sub.add_parser("get", help="Get one spec.")
    add_path_argument(get)
    get.add_argument("--id", required=True)
    get.set_defaults(func=run_get)

    list_cmd = spec_sub.add_parser("list", help="List specs.")
    add_path_argument(list_cmd)
    list_cmd.set_defaults(func=run_list)

    update = spec_sub.add_parser("update", help="Update a repo-local spec.")
    add_path_argument(update)
    update.add_argument("--id", required=True)
    update.add_argument("--title", default=None)
    update.add_argument("--body-file", default=None)
    update.add_argument("--kind", choices=["normative", "operational", "repo-local"], default=None)
    update.add_argument("--status", choices=["draft", "in_review", "accepted", "rejected", "withdrawn", "superseded", "retired"], default=None)
    update.add_argument("--note", default=None, help="Optional lifecycle note.")
    update.set_defaults(func=run_update)

    set_status = spec_sub.add_parser("set-status", help="Set spec lifecycle status.")
    add_path_argument(set_status)
    set_status.add_argument("--id", required=True)
    set_status.add_argument("--status", required=True, choices=["draft", "in_review", "accepted", "rejected", "withdrawn", "superseded", "retired"])
    set_status.add_argument("--note", default=None, help="Optional lifecycle note.")
    set_status.set_defaults(func=run_set_status)

    supersede = spec_sub.add_parser("supersede", help="Supersede spec ids with another spec.")
    add_path_argument(supersede)
    supersede.add_argument("--id", required=True)
    supersede.add_argument("--supersedes", nargs="+", required=True)
    supersede.add_argument("--note", default=None, help="Optional lifecycle note.")
    supersede.set_defaults(func=run_supersede)

    delete = spec_sub.add_parser("delete", help="Delete a repo-local spec.")
    add_path_argument(delete)
    delete.add_argument("--id", required=True)
    delete.set_defaults(func=run_delete)

    sync = spec_sub.add_parser("sync", help="Sync packaged specs into the repo.")
    add_path_argument(sync)
    sync.set_defaults(func=run_sync)

    reserve = spec_sub.add_parser("reserve", help="Spec reservation operations.")
    reserve_sub = reserve.add_subparsers(dest="spec_reserve_command", required=True)
    reserve_create = reserve_sub.add_parser("create", help="Create a repo-local spec reservation.")
    add_path_argument(reserve_create)
    reserve_create.add_argument("--name", required=True)
    reserve_create.add_argument("--start", type=int, required=True)
    reserve_create.add_argument("--end", type=int, required=True)
    reserve_create.set_defaults(func=run_reserve_create)

    reserve_list = reserve_sub.add_parser("list", help="List spec reservations.")
    add_path_argument(reserve_list)
    reserve_list.set_defaults(func=run_reserve_list)


def run_create(args: argparse.Namespace) -> dict[str, object]:
    return create_document(
        args.path,
        "spec",
        title=args.title,
        slug=args.slug,
        body_file=args.body_file,
        number=args.number,
        origin=args.origin,
        reserve_range=args.reserve_range,
        status=args.status,
        note=args.note,
        spec_kind=args.kind,
    )


def run_get(args: argparse.Namespace) -> dict[str, object]:
    return get_document(args.path, "spec", args.id)


def run_list(args: argparse.Namespace) -> dict[str, object]:
    return list_documents(args.path, "spec")


def run_update(args: argparse.Namespace) -> dict[str, object]:
    changes = compact_dict({"title": args.title, "body_file": args.body_file, "spec_kind": args.kind, "status": args.status, "note": args.note})
    if not changes:
        raise ValueError("At least one update field is required")
    return update_document(args.path, "spec", args.id, **changes)


def run_set_status(args: argparse.Namespace) -> dict[str, object]:
    return set_document_status(args.path, "spec", args.id, status=args.status, note=args.note)


def run_supersede(args: argparse.Namespace) -> dict[str, object]:
    return supersede_documents(args.path, "spec", args.id, supersedes=args.supersedes, note=args.note)


def run_delete(args: argparse.Namespace) -> dict[str, object]:
    return delete_document(args.path, "spec", args.id)


def run_sync(args: argparse.Namespace) -> dict[str, object]:
    return sync_documents(args.path, "spec")


def run_reserve_create(args: argparse.Namespace) -> dict[str, object]:
    return create_document_reservation(args.path, "spec", name=args.name, start=args.start, end=args.end)


def run_reserve_list(args: argparse.Namespace) -> dict[str, object]:
    return list_document_reservations(args.path, "spec")
