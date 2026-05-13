from __future__ import annotations

import argparse

from ssot_registry.api import ensure_repo_config, load_repo_config, validate_repo_config

from .common import add_path_argument


def register_config(subparsers: argparse._SubParsersAction) -> None:
    config = subparsers.add_parser(
        "config",
        help="Manage repo-local SSOT policy configuration.",
        description="Create, inspect, and validate the repo-local `.ssot/ssot.toml` policy file.",
    )
    config_sub = config.add_subparsers(dest="config_command", required=True)

    init = config_sub.add_parser(
        "init",
        help="Create or refresh the repo-local config file.",
        description="Ensure that `.ssot/ssot.toml` exists and contains a valid default template.",
    )
    add_path_argument(init)
    init.add_argument("--force", action="store_true", help="Overwrite an existing repo-local config file.")
    init.set_defaults(func=run_init)

    show = config_sub.add_parser(
        "show",
        help="Show the effective repo-local config.",
        description="Load and display the validated repo-local SSOT config.",
    )
    add_path_argument(show)
    show.set_defaults(func=run_show)

    validate = config_sub.add_parser(
        "validate",
        help="Validate the repo-local config.",
        description="Parse and validate the repo-local SSOT config file without mutating the repository.",
    )
    add_path_argument(validate)
    validate.set_defaults(func=run_validate)


def run_init(args: argparse.Namespace) -> dict[str, object]:
    return ensure_repo_config(args.path, overwrite=args.force)


def run_show(args: argparse.Namespace) -> dict[str, object]:
    return load_repo_config(args.path)


def run_validate(args: argparse.Namespace) -> dict[str, object]:
    return validate_repo_config(args.path)
