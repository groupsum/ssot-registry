from __future__ import annotations

import argparse
import json
from typing import Any

from ssot_registry.util.errors import GuardError, RegistryError, ValidationError

from .boundary_cmd import register_boundary
from .claim_cmd import register_claim
from .evidence_cmd import register_evidence
from .feature_cmd import register_feature
from .graph_cmd import register_graph
from .init_cmd import register_init
from .issue_cmd import register_issue
from .release_cmd import register_release
from .risk_cmd import register_risk
from .test_cmd import register_test
from .validate_cmd import register_validate


def _print(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=False))


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="ssot-registry",
        description="Portable single-source-of-truth registry for features, tests, claims, evidence, issues, risks, boundaries, and releases.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    register_init(subparsers)
    register_validate(subparsers)
    register_feature(subparsers)
    register_test(subparsers)
    register_issue(subparsers)
    register_claim(subparsers)
    register_evidence(subparsers)
    register_risk(subparsers)
    register_boundary(subparsers)
    register_release(subparsers)
    register_graph(subparsers)

    args = parser.parse_args()

    try:
        payload = args.func(args)
    except (RegistryError, ValidationError, GuardError, ValueError, FileNotFoundError) as exc:
        _print({"passed": False, "error": str(exc)})
        return 1

    _print(payload)
    return 0 if payload.get("passed", False) else 1
