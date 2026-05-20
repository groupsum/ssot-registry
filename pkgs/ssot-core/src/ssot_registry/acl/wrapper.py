from __future__ import annotations

import argparse
from pathlib import Path

from .policy import AclPolicy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Narrow ACL helper for SSOT path lease grants and revocations.")
    parser.add_argument("action", choices=["grant", "revoke"])
    parser.add_argument("repo_root")
    parser.add_argument("worker_user")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    policy = AclPolicy(Path(args.repo_root))
    commands = (
        policy.grant_commands(args.worker_user, args.paths)
        if args.action == "grant"
        else policy.revoke_commands(args.worker_user, args.paths)
    )
    if args.dry_run:
        for command in commands:
            print(" ".join(command.argv))
        return 0
    policy.apply(commands)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
