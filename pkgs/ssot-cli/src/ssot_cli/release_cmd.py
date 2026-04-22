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
from ssot_cli.common import add_ids_argument, add_path_argument, compact_dict


def register_release(subparsers: argparse._SubParsersAction) -> None:
    release = subparsers.add_parser(
        "release",
        help="Release operations.",
        description="Releases are publication units tied to a boundary and the claims and evidence required for certification, promotion, and publication.",
    )
    release_sub = release.add_subparsers(dest="release_command", required=True)

    create = release_sub.add_parser("create", help="Create a release candidate.", description="Create a release record tied to a frozen boundary and optional supporting claims and evidence.")
    add_path_argument(create)
    create.add_argument("--id", required=True, help="Normalized release id to create.")
    create.add_argument("--version", required=True, help="Semantic or operator-defined version string for the release.")
    create.add_argument("--status", choices=["draft", "candidate", "certified", "promoted", "published", "revoked"], default="draft", help="Current publication stage of the release.")
    create.add_argument("--boundary-id", required=True, help="Frozen boundary id that defines the release scope.")
    create.add_argument("--claim-ids", nargs="*", default=[], help="Claim ids bundled into the release.")
    create.add_argument("--evidence-ids", nargs="*", default=[], help="Evidence ids bundled into the release.")
    create.set_defaults(func=run_create)

    get = release_sub.add_parser("get", help="Show one release.", description="Fetch a single release record by id.")
    add_path_argument(get)
    get.add_argument("--id", required=True, help="Release id to retrieve.")
    get.set_defaults(func=run_get)

    list_cmd = release_sub.add_parser("list", help="List releases.", description="List release records currently known to the registry.")
    add_path_argument(list_cmd)
    add_ids_argument(list_cmd, help_text="Release ids to include in the list output.")
    list_cmd.set_defaults(func=run_list)

    update = release_sub.add_parser("update", help="Edit release metadata.", description="Update mutable release fields without changing its claim or evidence membership lists.")
    add_path_argument(update)
    update.add_argument("--id", required=True, help="Release id to update.")
    update.add_argument("--version", default=None, help="Replacement release version string.")
    update.add_argument("--status", choices=["draft", "candidate", "certified", "promoted", "published", "revoked"], default=None, help="Updated publication stage.")
    update.add_argument("--boundary-id", default=None, help="Replacement boundary id that defines the release scope.")
    update.set_defaults(func=run_update)

    delete = release_sub.add_parser("delete", help="Delete a release.", description="Remove a release record from the registry.")
    add_path_argument(delete)
    delete.add_argument("--id", required=True, help="Release id to delete.")
    delete.set_defaults(func=run_delete)

    add_claim = release_sub.add_parser("add-claim", help="Attach claims to a release.", description="Add one or more claim ids to the release evidence package.")
    add_path_argument(add_claim)
    add_claim.add_argument("--id", required=True, help="Release id that should receive the claims.")
    add_claim.add_argument("--claim-ids", nargs="+", required=True, help="Claim ids to attach to the release.")
    add_claim.set_defaults(func=run_add_claim)

    remove_claim = release_sub.add_parser("remove-claim", help="Remove claims from a release.", description="Remove one or more claim ids from the release evidence package.")
    add_path_argument(remove_claim)
    remove_claim.add_argument("--id", required=True, help="Release id whose claims should be removed.")
    remove_claim.add_argument("--claim-ids", nargs="+", required=True, help="Claim ids to remove from the release.")
    remove_claim.set_defaults(func=run_remove_claim)

    add_evidence = release_sub.add_parser("add-evidence", help="Attach evidence to a release.", description="Add one or more evidence ids to the release evidence package.")
    add_path_argument(add_evidence)
    add_evidence.add_argument("--id", required=True, help="Release id that should receive the evidence.")
    add_evidence.add_argument("--evidence-ids", nargs="+", required=True, help="Evidence ids to attach to the release.")
    add_evidence.set_defaults(func=run_add_evidence)

    remove_evidence = release_sub.add_parser("remove-evidence", help="Remove evidence from a release.", description="Remove one or more evidence ids from the release evidence package.")
    add_path_argument(remove_evidence)
    remove_evidence.add_argument("--id", required=True, help="Release id whose evidence should be removed.")
    remove_evidence.add_argument("--evidence-ids", nargs="+", required=True, help="Evidence ids to remove from the release.")
    remove_evidence.set_defaults(func=run_remove_evidence)

    certify = release_sub.add_parser("certify", help="Run release certification.", description="Evaluate release guards and certify the release when all required checks pass.")
    add_path_argument(certify)
    certify.add_argument("--release-id", default=None, help="Release id to certify. Omit to use the active release.")
    certify.add_argument("--write-report", action="store_true", help="Write the certification report to the repository for audit review.")
    certify.set_defaults(func=run_certify)

    promote = release_sub.add_parser("promote", help="Promote a certified release.", description="Advance a certified release to the promoted state and emit a snapshot.")
    add_path_argument(promote)
    promote.add_argument("--release-id", default=None, help="Release id to promote. Omit to use the active release.")
    promote.set_defaults(func=run_promote)

    publish = release_sub.add_parser("publish", help="Publish a promoted release.", description="Advance a promoted release to the published state and emit a published snapshot.")
    add_path_argument(publish)
    publish.add_argument("--release-id", default=None, help="Release id to publish. Omit to use the active release.")
    publish.set_defaults(func=run_publish)

    revoke = release_sub.add_parser("revoke", help="Revoke a release.", description="Mark a release revoked and record the reason for operators and auditors.")
    add_path_argument(revoke)
    revoke.add_argument("--release-id", required=True, help="Release id to revoke.")
    revoke.add_argument("--reason", required=True, help="Operator-facing reason explaining the revocation.")
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
    return list_entities(args.path, "releases", ids=args.ids)


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

