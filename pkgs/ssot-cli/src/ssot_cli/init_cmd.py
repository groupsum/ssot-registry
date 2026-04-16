from __future__ import annotations

import argparse

from ssot_registry.api import initialize_repo


def register_init(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("init", help="Initialize a normalized .ssot tree in a repository.")
    parser.add_argument("path", nargs="?", default=".", help="Repository root.")
    parser.add_argument("--repo-id", default="repo:example", help="Normalized repository id.")
    parser.add_argument("--repo-name", default="example", help="Repository name.")
    parser.add_argument("--version", default="0.1.0", help="Initial release version.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing registry.")
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> dict[str, object]:
    return initialize_repo(
        path=args.path,
        repo_id=args.repo_id,
        repo_name=args.repo_name,
        version=args.version,
        force=args.force,
    )
