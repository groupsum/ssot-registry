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
from ssot_cli.common import add_ids_argument, add_path_argument, compact_dict


def register_adr(subparsers: argparse._SubParsersAction) -> None:
    adr = subparsers.add_parser(
        "adr",
        help="ADR operations.",
        description="Architectural decision records capture why the system is designed the way it is and preserve decision history.",
    )
    adr_sub = adr.add_subparsers(dest="adr_command", required=True)

    create = adr_sub.add_parser(
        "create",
        help="Author a new architectural decision record.",
        description="Create an ADR that captures a design decision, its rationale, and its document source.",
    )
    add_path_argument(create)
    create.add_argument("--title", required=True, help="Human-readable ADR title shown to operators and reviewers.")
    create.add_argument("--slug", required=True, help="Stable slug used to derive the ADR document id and filename.")
    create.add_argument("--body", default=None, help="Inline ADR body text to persist without a separate authored payload file.")
    create.add_argument("--body-file", default=None, help="Path to the ADR YAML or JSON body payload to import into the registry.")
    create.add_argument("--number", type=int, default=None, help="Explicit ADR number to assign instead of auto-allocation.")
    create.add_argument("--status", choices=["draft", "in_review", "accepted", "rejected", "withdrawn", "superseded", "retired"], default="draft", help="Current decision lifecycle state for the ADR.")
    create.add_argument("--note", default=None, help="Lifecycle note that explains review, acceptance, or retirement context.")
    create.add_argument("--origin", choices=["repo-local", "ssot-origin", "ssot-core"], default="repo-local", help="Source authority for the ADR document.")
    create.add_argument("--reserve-range", default=None, help="Named reservation range to allocate the ADR number from.")
    create.set_defaults(func=run_create)

    get = adr_sub.add_parser("get", help="Show one ADR.", description="Fetch a single ADR by id for review or automation.")
    add_path_argument(get)
    get.add_argument("--id", required=True, help="ADR id to retrieve.")
    get.set_defaults(func=run_get)

    list_cmd = adr_sub.add_parser("list", help="List ADRs.", description="List ADR documents currently known to the registry.")
    add_path_argument(list_cmd)
    add_ids_argument(list_cmd, help_text="ADR ids to include in the list output.")
    list_cmd.set_defaults(func=run_list)

    update = adr_sub.add_parser(
        "update",
        help="Edit a repo-local ADR.",
        description="Update mutable ADR fields such as title, body source, status, or lifecycle note.",
    )
    add_path_argument(update)
    update.add_argument("--id", required=True, help="ADR id to update.")
    update.add_argument("--title", default=None, help="Replacement ADR title.")
    update.add_argument("--body", default=None, help="Replacement inline ADR body text.")
    update.add_argument("--body-file", default=None, help="Replacement ADR body file to ingest.")
    update.add_argument("--status", choices=["draft", "in_review", "accepted", "rejected", "withdrawn", "superseded", "retired"], default=None, help="New lifecycle state for the ADR.")
    update.add_argument("--note", default=None, help="Updated lifecycle note or rationale.")
    update.set_defaults(func=run_update)

    set_status = adr_sub.add_parser(
        "set-status",
        help="Advance or revise ADR status.",
        description="Change the lifecycle state of an ADR without editing other document fields.",
    )
    add_path_argument(set_status)
    set_status.add_argument("--id", required=True, help="ADR id whose status should change.")
    set_status.add_argument("--status", required=True, choices=["draft", "in_review", "accepted", "rejected", "withdrawn", "superseded", "retired"], help="Target lifecycle state to set.")
    set_status.add_argument("--note", default=None, help="Reason or context for the status transition.")
    set_status.set_defaults(func=run_set_status)

    supersede = adr_sub.add_parser(
        "supersede",
        help="Mark older ADRs as replaced.",
        description="Record that one ADR supersedes one or more earlier ADRs.",
    )
    add_path_argument(supersede)
    supersede.add_argument("--id", required=True, help="Newer ADR that supersedes prior decisions.")
    supersede.add_argument("--supersedes", nargs="+", required=True, help="ADR ids that are being replaced by `--id`.")
    supersede.add_argument("--note", default=None, help="Transition note explaining why the older ADRs were superseded.")
    supersede.set_defaults(func=run_supersede)

    delete = adr_sub.add_parser("delete", help="Delete a repo-local ADR.", description="Remove a repo-local ADR entry and its associated document metadata.")
    add_path_argument(delete)
    delete.add_argument("--id", required=True, help="ADR id to delete.")
    delete.set_defaults(func=run_delete)

    sync = adr_sub.add_parser("sync", help="Refresh packaged ADRs.", description="Sync packaged ADR documents from installed sources into the repository.")
    add_path_argument(sync)
    sync.set_defaults(func=run_sync)

    reserve = adr_sub.add_parser("reserve", help="Manage ADR number ranges.", description="Reserve ADR number ranges for a team, owner, or local namespace.")
    reserve_sub = reserve.add_subparsers(dest="adr_reserve_command", required=True)
    reserve_create = reserve_sub.add_parser("create", help="Reserve ADR numbers.", description="Create a repo-local reservation range for ADR numbering.")
    add_path_argument(reserve_create)
    reserve_create.add_argument("--name", required=True, help="Reservation owner or label.")
    reserve_create.add_argument("--start", type=int, required=True, help="First ADR number included in the reservation.")
    reserve_create.add_argument("--end", type=int, required=True, help="Last ADR number included in the reservation.")
    reserve_create.set_defaults(func=run_reserve_create)

    reserve_list = reserve_sub.add_parser("list", help="List ADR reservations.", description="Show ADR numbering reservations currently defined in the repository.")
    add_path_argument(reserve_list)
    reserve_list.set_defaults(func=run_reserve_list)


def run_create(args: argparse.Namespace) -> dict[str, object]:
    return create_document(
        args.path,
        "adr",
        title=args.title,
        slug=args.slug,
        body=args.body,
        body_file=args.body_file,
        number=args.number,
        origin=args.origin,
        reserve_range=args.reserve_range,
        status=args.status,
        note=args.note,
    )


def run_get(args: argparse.Namespace) -> dict[str, object]:
    return get_document(args.path, "adr", args.id)


def run_list(args: argparse.Namespace) -> dict[str, object]:
    return list_documents(args.path, "adr", ids=args.ids)


def run_update(args: argparse.Namespace) -> dict[str, object]:
    changes = compact_dict({"title": args.title, "body": args.body, "body_file": args.body_file, "status": args.status, "note": args.note})
    if not changes:
        raise ValueError("At least one update field is required")
    return update_document(args.path, "adr", args.id, **changes)


def run_set_status(args: argparse.Namespace) -> dict[str, object]:
    return set_document_status(args.path, "adr", args.id, status=args.status, note=args.note)


def run_supersede(args: argparse.Namespace) -> dict[str, object]:
    return supersede_documents(args.path, "adr", args.id, supersedes=args.supersedes, note=args.note)


def run_delete(args: argparse.Namespace) -> dict[str, object]:
    return delete_document(args.path, "adr", args.id)


def run_sync(args: argparse.Namespace) -> dict[str, object]:
    return sync_documents(args.path, "adr")


def run_reserve_create(args: argparse.Namespace) -> dict[str, object]:
    return create_document_reservation(args.path, "adr", name=args.name, start=args.start, end=args.end)


def run_reserve_list(args: argparse.Namespace) -> dict[str, object]:
    return list_document_reservations(args.path, "adr")

