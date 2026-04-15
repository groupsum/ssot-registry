from __future__ import annotations

import argparse

from ssot_registry.api import (
    create_document,
    create_document_reservation,
    delete_document,
    get_document,
    list_document_reservations,
    list_documents,
    sync_documents,
    update_document,
)
from ssot_registry.cli.common import add_path_argument, compact_dict


def register_adr(subparsers: argparse._SubParsersAction) -> None:
    adr = subparsers.add_parser("adr", help="ADR operations.")
    adr_sub = adr.add_subparsers(dest="adr_command", required=True)

    create = adr_sub.add_parser("create", help="Create a repo-local ADR.")
    add_path_argument(create)
    create.add_argument("--title", required=True)
    create.add_argument("--slug", required=True)
    create.add_argument("--body-file", required=True)
    create.add_argument("--number", type=int, default=None)
    create.add_argument("--status", choices=["proposed", "accepted", "superseded", "retired"], default="proposed")
    create.add_argument("--origin", choices=["repo-local"], default="repo-local")
    create.add_argument("--reserve-range", default=None, help="Reservation owner to allocate from.")
    create.set_defaults(func=run_create)

    get = adr_sub.add_parser("get", help="Get one ADR.")
    add_path_argument(get)
    get.add_argument("--id", required=True)
    get.set_defaults(func=run_get)

    list_cmd = adr_sub.add_parser("list", help="List ADRs.")
    add_path_argument(list_cmd)
    list_cmd.set_defaults(func=run_list)

    update = adr_sub.add_parser("update", help="Update a repo-local ADR.")
    add_path_argument(update)
    update.add_argument("--id", required=True)
    update.add_argument("--title", default=None)
    update.add_argument("--body-file", default=None)
    update.add_argument("--status", choices=["proposed", "accepted", "superseded", "retired"], default=None)
    update.set_defaults(func=run_update)

    delete = adr_sub.add_parser("delete", help="Delete a repo-local ADR.")
    add_path_argument(delete)
    delete.add_argument("--id", required=True)
    delete.set_defaults(func=run_delete)

    sync = adr_sub.add_parser("sync", help="Sync packaged ADRs into the repo.")
    add_path_argument(sync)
    sync.set_defaults(func=run_sync)

    reserve = adr_sub.add_parser("reserve", help="ADR reservation operations.")
    reserve_sub = reserve.add_subparsers(dest="adr_reserve_command", required=True)
    reserve_create = reserve_sub.add_parser("create", help="Create a repo-local ADR reservation.")
    add_path_argument(reserve_create)
    reserve_create.add_argument("--name", required=True)
    reserve_create.add_argument("--start", type=int, required=True)
    reserve_create.add_argument("--end", type=int, required=True)
    reserve_create.set_defaults(func=run_reserve_create)

    reserve_list = reserve_sub.add_parser("list", help="List ADR reservations.")
    add_path_argument(reserve_list)
    reserve_list.set_defaults(func=run_reserve_list)


def run_create(args: argparse.Namespace) -> dict[str, object]:
    return create_document(
        args.path,
        "adr",
        title=args.title,
        slug=args.slug,
        body_file=args.body_file,
        number=args.number,
        origin=args.origin,
        reserve_range=args.reserve_range,
        status=args.status,
    )


def run_get(args: argparse.Namespace) -> dict[str, object]:
    return get_document(args.path, "adr", args.id)


def run_list(args: argparse.Namespace) -> dict[str, object]:
    return list_documents(args.path, "adr")


def run_update(args: argparse.Namespace) -> dict[str, object]:
    changes = compact_dict({"title": args.title, "body_file": args.body_file, "status": args.status})
    if not changes:
        raise ValueError("At least one update field is required")
    return update_document(args.path, "adr", args.id, **changes)


def run_delete(args: argparse.Namespace) -> dict[str, object]:
    return delete_document(args.path, "adr", args.id)


def run_sync(args: argparse.Namespace) -> dict[str, object]:
    return sync_documents(args.path, "adr")


def run_reserve_create(args: argparse.Namespace) -> dict[str, object]:
    return create_document_reservation(args.path, "adr", name=args.name, start=args.start, end=args.end)


def run_reserve_list(args: argparse.Namespace) -> dict[str, object]:
    return list_document_reservations(args.path, "adr")
