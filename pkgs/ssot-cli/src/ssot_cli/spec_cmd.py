from __future__ import annotations

import argparse

from ssot_registry.api import (
    add_spec_adr_links,
    create_document,
    create_document_reservation,
    delete_document,
    get_document,
    list_document_reservations,
    list_documents,
    remove_spec_adr_links,
    set_document_status,
    sync_documents,
    supersede_documents,
    update_document,
)
from ssot_cli.common import add_ids_argument, add_path_argument, compact_dict


def register_spec(subparsers: argparse._SubParsersAction) -> None:
    spec = subparsers.add_parser(
        "spec",
        help="Manage specification documents.",
        description="SPEC documents define the normative or operational contract, alongside governance and local-policy contracts that repositories are expected to satisfy.",
    )
    spec_sub = spec.add_subparsers(dest="spec_command", required=True)

    create = spec_sub.add_parser(
        "create",
        help="Author a new SPEC document.",
        description="Create a SPEC document and register its lifecycle, source, and kind metadata.",
    )
    add_path_argument(create)
    create.add_argument("--title", required=True, help="Human-readable SPEC title.")
    create.add_argument("--slug", required=True, help="Stable slug used to derive the SPEC id and filename.")
    create.add_argument("--body", default=None, help="Inline SPEC body text to persist without a separate authored payload file.")
    create.add_argument("--body-file", default=None, help="Path to the SPEC YAML or JSON body payload to import.")
    create.add_argument("--number", type=int, default=None, help="Explicit SPEC number to assign instead of auto-allocation.")
    create.add_argument("--origin", choices=["repo-local", "ssot-origin", "ssot-core"], default="repo-local", help="Source authority that owns this SPEC.")
    create.add_argument("--kind", choices=["normative", "operational", "governance", "local-policy"], default="local-policy", help="Contract role the SPEC plays for operators and implementers.")
    create.add_argument("--status", choices=["draft", "in_review", "accepted", "rejected", "withdrawn", "superseded", "retired"], default="draft", help="Current lifecycle state of the SPEC.")
    create.add_argument("--note", default=None, help="Lifecycle note explaining the SPEC state or transition.")
    create.add_argument("--reserve-range", default=None, help="Named reservation range to allocate the SPEC number from.")
    create.add_argument("--adr-ids", nargs="*", default=None, help="ADR ids that typedly govern or motivate the SPEC.")
    create.set_defaults(func=run_create)

    get = spec_sub.add_parser("get", help="Show one SPEC.", description="Fetch a single SPEC by id.")
    add_path_argument(get)
    get.add_argument("--id", required=True, help="SPEC id to retrieve.")
    get.set_defaults(func=run_get)

    list_cmd = spec_sub.add_parser("list", help="List SPECs.", description="List SPEC documents currently registered.")
    add_path_argument(list_cmd)
    add_ids_argument(list_cmd, help_text="SPEC ids to include in the list output.")
    list_cmd.set_defaults(func=run_list)

    link = spec_sub.add_parser("link", help="Attach ADRs to a SPEC.", description="Add typed ADR references to a SPEC without changing other document fields.")
    add_path_argument(link)
    link.add_argument("--id", required=True, help="SPEC id that should receive ADR links.")
    link.add_argument("--adr-ids", nargs="+", required=True, help="ADR ids to attach.")
    link.set_defaults(func=run_link)

    unlink = spec_sub.add_parser("unlink", help="Remove ADRs from a SPEC.", description="Remove typed ADR references from a SPEC without changing other document fields.")
    add_path_argument(unlink)
    unlink.add_argument("--id", required=True, help="SPEC id whose ADR links should be removed.")
    unlink.add_argument("--adr-ids", nargs="+", required=True, help="ADR ids to detach.")
    unlink.set_defaults(func=run_unlink)

    update = spec_sub.add_parser("update", help="Edit a SPEC.", description="Update mutable SPEC fields such as title, body source, kind, or lifecycle state.")
    add_path_argument(update)
    update.add_argument("--id", required=True, help="SPEC id to update.")
    update.add_argument("--title", default=None, help="Replacement SPEC title.")
    update.add_argument("--body", default=None, help="Replacement inline SPEC body text.")
    update.add_argument("--body-file", default=None, help="Replacement SPEC body file to ingest.")
    update.add_argument("--kind", choices=["normative", "operational", "governance", "local-policy"], default=None, help="Replacement contract kind.")
    update.add_argument("--adr-ids", nargs="*", default=None, help="Replacement typed ADR ids for the SPEC.")
    update.add_argument("--status", choices=["draft", "in_review", "accepted", "rejected", "withdrawn", "superseded", "retired"], default=None, help="New lifecycle state.")
    update.add_argument("--note", default=None, help="Updated lifecycle note or rationale.")
    update.set_defaults(func=run_update)

    set_status = spec_sub.add_parser("set-status", help="Advance or revise SPEC status.", description="Change the lifecycle state of a SPEC without editing other document fields.")
    add_path_argument(set_status)
    set_status.add_argument("--id", required=True, help="SPEC id whose status should change.")
    set_status.add_argument("--status", required=True, choices=["draft", "in_review", "accepted", "rejected", "withdrawn", "superseded", "retired"], help="Target lifecycle state to set.")
    set_status.add_argument("--note", default=None, help="Reason or context for the status transition.")
    set_status.set_defaults(func=run_set_status)

    supersede = spec_sub.add_parser("supersede", help="Mark older SPECs as replaced.", description="Record that one SPEC supersedes one or more prior SPEC documents.")
    add_path_argument(supersede)
    supersede.add_argument("--id", required=True, help="Newer SPEC that supersedes prior documents.")
    supersede.add_argument("--supersedes", nargs="+", required=True, help="SPEC ids that are being replaced by `--id`.")
    supersede.add_argument("--note", default=None, help="Transition note explaining the supersedure.")
    supersede.set_defaults(func=run_supersede)

    delete = spec_sub.add_parser("delete", help="Delete a repo-local SPEC.", description="Remove a repo-local SPEC entry and its associated document metadata.")
    add_path_argument(delete)
    delete.add_argument("--id", required=True, help="SPEC id to delete.")
    delete.set_defaults(func=run_delete)

    sync = spec_sub.add_parser("sync", help="Refresh packaged SPECs.", description="Sync packaged SPEC documents from installed sources into the repository.")
    add_path_argument(sync)
    sync.set_defaults(func=run_sync)

    reserve = spec_sub.add_parser("reserve", help="Manage SPEC number ranges.", description="Reserve SPEC number ranges for a team, owner, or local namespace.")
    reserve_sub = reserve.add_subparsers(dest="spec_reserve_command", required=True)
    reserve_create = reserve_sub.add_parser("create", help="Reserve SPEC numbers.", description="Create a repo-local reservation range for SPEC numbering.")
    add_path_argument(reserve_create)
    reserve_create.add_argument("--name", required=True, help="Reservation owner or label.")
    reserve_create.add_argument("--start", type=int, required=True, help="First SPEC number included in the reservation.")
    reserve_create.add_argument("--end", type=int, required=True, help="Last SPEC number included in the reservation.")
    reserve_create.set_defaults(func=run_reserve_create)

    reserve_list = reserve_sub.add_parser("list", help="List SPEC reservations.", description="Show SPEC numbering reservations currently defined in the repository.")
    add_path_argument(reserve_list)
    reserve_list.set_defaults(func=run_reserve_list)


def run_create(args: argparse.Namespace) -> dict[str, object]:
    return create_document(
        args.path,
        "spec",
        title=args.title,
        slug=args.slug,
        body=args.body,
        body_file=args.body_file,
        number=args.number,
        origin=args.origin,
        reserve_range=args.reserve_range,
        status=args.status,
        note=args.note,
        spec_kind=args.kind,
        adr_ids=args.adr_ids,
    )


def run_get(args: argparse.Namespace) -> dict[str, object]:
    return get_document(args.path, "spec", args.id)


def run_list(args: argparse.Namespace) -> dict[str, object]:
    return list_documents(args.path, "spec", ids=args.ids)


def run_link(args: argparse.Namespace) -> dict[str, object]:
    return add_spec_adr_links(args.path, args.id, args.adr_ids)


def run_unlink(args: argparse.Namespace) -> dict[str, object]:
    return remove_spec_adr_links(args.path, args.id, args.adr_ids)


def run_update(args: argparse.Namespace) -> dict[str, object]:
    changes = compact_dict(
        {
            "title": args.title,
            "body": args.body,
            "body_file": args.body_file,
            "spec_kind": args.kind,
            "adr_ids": args.adr_ids,
            "status": args.status,
            "note": args.note,
        }
    )
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

