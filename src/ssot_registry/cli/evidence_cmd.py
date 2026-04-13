from __future__ import annotations

import argparse

from ssot_registry.api import verify_evidence_rows


def register_evidence(subparsers: argparse._SubParsersAction) -> None:
    evidence = subparsers.add_parser("evidence", help="Evidence operations.")
    evidence_sub = evidence.add_subparsers(dest="evidence_command", required=True)

    verify = evidence_sub.add_parser("verify", help="Verify one evidence row or all evidence rows.")
    verify.add_argument("path", nargs="?", default=".", help="Registry file path or repository root.")
    verify.add_argument("--evidence-id", default=None, help="Evidence id to verify. Omit to verify all rows.")
    verify.set_defaults(func=run_verify)


def run_verify(args: argparse.Namespace) -> dict[str, object]:
    return verify_evidence_rows(path=args.path, evidence_id=args.evidence_id)
