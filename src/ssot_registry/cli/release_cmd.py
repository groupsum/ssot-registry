from __future__ import annotations

import argparse

from ssot_registry.api import certify_release, promote_release, publish_release, revoke_release


def register_release(subparsers: argparse._SubParsersAction) -> None:
    release = subparsers.add_parser("release", help="Release operations.")
    release_sub = release.add_subparsers(dest="release_command", required=True)

    certify = release_sub.add_parser("certify", help="Certify a release after guard checks pass.")
    certify.add_argument("path", nargs="?", default=".", help="Registry file path or repository root.")
    certify.add_argument("--release-id", default=None, help="Release id. Defaults to the active release.")
    certify.add_argument("--write-report", action="store_true", help="Write certification report.")
    certify.set_defaults(func=run_certify)

    promote = release_sub.add_parser("promote", help="Promote a certified release and emit a snapshot.")
    promote.add_argument("path", nargs="?", default=".", help="Registry file path or repository root.")
    promote.add_argument("--release-id", default=None, help="Release id. Defaults to the active release.")
    promote.set_defaults(func=run_promote)

    publish = release_sub.add_parser("publish", help="Publish a promoted release and emit a published snapshot.")
    publish.add_argument("path", nargs="?", default=".", help="Registry file path or repository root.")
    publish.add_argument("--release-id", default=None, help="Release id. Defaults to the active release.")
    publish.set_defaults(func=run_publish)

    revoke = release_sub.add_parser("revoke", help="Revoke a release.")
    revoke.add_argument("path", nargs="?", default=".", help="Registry file path or repository root.")
    revoke.add_argument("--release-id", required=True, help="Release id to revoke.")
    revoke.add_argument("--reason", required=True, help="Revocation reason.")
    revoke.set_defaults(func=run_revoke)


def run_certify(args: argparse.Namespace) -> dict[str, object]:
    return certify_release(path=args.path, release_id=args.release_id, write_report=args.write_report)


def run_promote(args: argparse.Namespace) -> dict[str, object]:
    return promote_release(path=args.path, release_id=args.release_id)


def run_publish(args: argparse.Namespace) -> dict[str, object]:
    return publish_release(path=args.path, release_id=args.release_id)


def run_revoke(args: argparse.Namespace) -> dict[str, object]:
    return revoke_release(path=args.path, release_id=args.release_id, reason=args.reason)
