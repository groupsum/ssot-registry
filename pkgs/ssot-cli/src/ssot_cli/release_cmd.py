from __future__ import annotations

import argparse

from ssot_registry.api import (
    add_release_claims,
    add_release_evidence,
    certify_release,
    create_entity,
    delete_entity,
    get_entity,
    list_entities,
    promote_release,
    publish_release,
    remove_release_claims,
    remove_release_evidence,
    revoke_release,
    update_entity,
)
from ssot_cli.common import add_path_argument, compact_dict


def register_release(subparsers: argparse._SubParsersAction) -> None:
    release = subparsers.add_parser("release", help="Release operations.")
    release_sub = release.add_subparsers(dest="release_command", required=True)

    create = release_sub.add_parser("create", help="Create a release.")
    add_path_argument(create)
    create.add_argument("--id", required=True)
    create.add_argument("--version", required=True)
    create.add_argument("--status", choices=["draft", "candidate", "certified", "promoted", "published", "revoked"], default="draft")
    create.add_argument("--boundary-id", required=True)
    create.add_argument("--claim-ids", nargs="*", default=[])
    create.add_argument("--evidence-ids", nargs="*", default=[])
    create.set_defaults(func=run_create)

    get = release_sub.add_parser("get", help="Get one release.")
    add_path_argument(get)
    get.add_argument("--id", required=True)
    get.set_defaults(func=run_get)

    list_cmd = release_sub.add_parser("list", help="List releases.")
    add_path_argument(list_cmd)
    list_cmd.set_defaults(func=run_list)

    update = release_sub.add_parser("update", help="Update release fields.")
    add_path_argument(update)
    update.add_argument("--id", required=True)
    update.add_argument("--version", default=None)
    update.add_argument("--status", choices=["draft", "candidate", "certified", "promoted", "published", "revoked"], default=None)
    update.add_argument("--boundary-id", default=None)
    update.set_defaults(func=run_update)

    delete = release_sub.add_parser("delete", help="Delete a release.")
    add_path_argument(delete)
    delete.add_argument("--id", required=True)
    delete.set_defaults(func=run_delete)

    add_claim = release_sub.add_parser("add-claim", help="Add claim ids to a release.")
    add_path_argument(add_claim)
    add_claim.add_argument("--id", required=True)
    add_claim.add_argument("--claim-ids", nargs="+", required=True)
    add_claim.set_defaults(func=run_add_claim)

    remove_claim = release_sub.add_parser("remove-claim", help="Remove claim ids from a release.")
    add_path_argument(remove_claim)
    remove_claim.add_argument("--id", required=True)
    remove_claim.add_argument("--claim-ids", nargs="+", required=True)
    remove_claim.set_defaults(func=run_remove_claim)

    add_evidence = release_sub.add_parser("add-evidence", help="Add evidence ids to a release.")
    add_path_argument(add_evidence)
    add_evidence.add_argument("--id", required=True)
    add_evidence.add_argument("--evidence-ids", nargs="+", required=True)
    add_evidence.set_defaults(func=run_add_evidence)

    remove_evidence = release_sub.add_parser("remove-evidence", help="Remove evidence ids from a release.")
    add_path_argument(remove_evidence)
    remove_evidence.add_argument("--id", required=True)
    remove_evidence.add_argument("--evidence-ids", nargs="+", required=True)
    remove_evidence.set_defaults(func=run_remove_evidence)

    certify = release_sub.add_parser("certify", help="Certify a release after guard checks pass.")
    add_path_argument(certify)
    certify.add_argument("--release-id", default=None, help="Release id. Defaults to the active release.")
    certify.add_argument("--write-report", action="store_true", help="Write certification report.")
    certify.set_defaults(func=run_certify)

    promote = release_sub.add_parser("promote", help="Promote a certified release and emit a snapshot.")
    add_path_argument(promote)
    promote.add_argument("--release-id", default=None, help="Release id. Defaults to the active release.")
    promote.set_defaults(func=run_promote)

    publish = release_sub.add_parser("publish", help="Publish a promoted release and emit a published snapshot.")
    add_path_argument(publish)
    publish.add_argument("--release-id", default=None, help="Release id. Defaults to the active release.")
    publish.set_defaults(func=run_publish)

    revoke = release_sub.add_parser("revoke", help="Revoke a release.")
    add_path_argument(revoke)
    revoke.add_argument("--release-id", required=True, help="Release id to revoke.")
    revoke.add_argument("--reason", required=True, help="Revocation reason.")
    revoke.set_defaults(func=run_revoke)


def run_create(args: argparse.Namespace) -> dict[str, object]:
    row = {
        "id": args.id,
        "version": args.version,
        "status": args.status,
        "boundary_id": args.boundary_id,
        "claim_ids": args.claim_ids,
        "evidence_ids": args.evidence_ids,
    }
    return create_entity(args.path, "releases", row)


def run_get(args: argparse.Namespace) -> dict[str, object]:
    return get_entity(args.path, "releases", args.id)


def run_list(args: argparse.Namespace) -> dict[str, object]:
    return list_entities(args.path, "releases")


def run_update(args: argparse.Namespace) -> dict[str, object]:
    changes = compact_dict({"version": args.version, "status": args.status, "boundary_id": args.boundary_id})
    if not changes:
        raise ValueError("At least one update field is required")
    return update_entity(args.path, "releases", args.id, changes)


def run_delete(args: argparse.Namespace) -> dict[str, object]:
    return delete_entity(args.path, "releases", args.id)


def run_add_claim(args: argparse.Namespace) -> dict[str, object]:
    return add_release_claims(args.path, args.id, args.claim_ids)


def run_remove_claim(args: argparse.Namespace) -> dict[str, object]:
    return remove_release_claims(args.path, args.id, args.claim_ids)


def run_add_evidence(args: argparse.Namespace) -> dict[str, object]:
    return add_release_evidence(args.path, args.id, args.evidence_ids)


def run_remove_evidence(args: argparse.Namespace) -> dict[str, object]:
    return remove_release_evidence(args.path, args.id, args.evidence_ids)


def run_certify(args: argparse.Namespace) -> dict[str, object]:
    return certify_release(path=args.path, release_id=args.release_id, write_report=args.write_report)


def run_promote(args: argparse.Namespace) -> dict[str, object]:
    return promote_release(path=args.path, release_id=args.release_id)


def run_publish(args: argparse.Namespace) -> dict[str, object]:
    return publish_release(path=args.path, release_id=args.release_id)


def run_revoke(args: argparse.Namespace) -> dict[str, object]:
    return revoke_release(path=args.path, release_id=args.release_id, reason=args.reason)

