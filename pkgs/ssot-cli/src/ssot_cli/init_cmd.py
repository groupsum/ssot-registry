from __future__ import annotations

import argparse

from ssot_registry.api import initialize_repo


def register_init(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "init",
        help="Create a new SSOT workspace in a repository.",
        description="Bootstrap the `.ssot` tree, starter registry, and baseline metadata for a repository.",
    )
    parser.add_argument("path", nargs="?", default=".", help="Repository root where the `.ssot` workspace should be created.")
    parser.add_argument("--repo-id", default="repo:example", help="Normalized repository identifier recorded in the registry.")
    parser.add_argument("--repo-name", default="example", help="Human-readable repository name recorded in the registry.")
    parser.add_argument("--version", default="0.1.0", help="Initial release version to seed into the repository metadata.")
    parser.add_argument("--force", action="store_true", help="Replace an existing registry at the target path.")
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> dict[str, object]:
    return initialize_repo(
        path=args.path,
        repo_id=args.repo_id,
        repo_name=args.repo_name,
        version=args.version,
        force=args.force,
    )
