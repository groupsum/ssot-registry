from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from ssot_registry.util.errors import GuardError, RegistryError, ValidationError
from ssot_registry.util.formatting import render_payload

from .adr_cmd import register_adr
from .boundary_cmd import register_boundary
from .claim_cmd import register_claim
from .evidence_cmd import register_evidence
from .feature_cmd import register_feature
from .graph_cmd import register_graph
from .init_cmd import register_init
from .issue_cmd import register_issue
from .profile_cmd import register_profile
from .registry_cmd import register_registry
from .release_cmd import register_release
from .risk_cmd import register_risk
from .spec_cmd import register_spec
from .test_cmd import register_test
from .upgrade_cmd import register_upgrade
from .validate_cmd import register_validate


def _default_prog() -> str:
    executable = Path(sys.argv[0]).name
    if executable.endswith(".exe"):
        executable = executable[:-4]
    if executable in {"", "__main__", "-m"}:
        return "ssot-registry"
    return executable


def build_parser(*, prog: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=prog or _default_prog(),
        description="Portable single-source-of-truth registry for features, tests, claims, evidence, issues, risks, boundaries, and releases.",
    )
    parser.add_argument("--output-format", default="json", choices=["json", "csv", "df", "yaml", "toml"], help="CLI output format.")
    parser.add_argument("--output-file", default=None, help="Optional file to write the rendered command output.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    register_init(subparsers)
    register_validate(subparsers)
    register_upgrade(subparsers)
    register_adr(subparsers)
    register_spec(subparsers)
    register_feature(subparsers)
    register_profile(subparsers)
    register_test(subparsers)
    register_issue(subparsers)
    register_claim(subparsers)
    register_evidence(subparsers)
    register_risk(subparsers)
    register_boundary(subparsers)
    register_release(subparsers)
    register_graph(subparsers)
    register_registry(subparsers)
    return parser


def _print(payload: dict[str, Any], output_format: str) -> None:
    print(render_payload(payload, output_format), end="")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        payload = args.func(args)
    except (RegistryError, ValidationError, GuardError, ValueError, FileNotFoundError) as exc:
        _print({"passed": False, "error": str(exc)}, args.output_format)
        return 1

    rendered = render_payload(payload, args.output_format)
    if args.output_file is not None:
        path = Path(args.output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if payload.get("passed", False) else 1
