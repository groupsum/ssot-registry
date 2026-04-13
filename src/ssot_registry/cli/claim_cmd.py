from __future__ import annotations

import argparse

from ssot_registry.api import evaluate_claims


def register_claim(subparsers: argparse._SubParsersAction) -> None:
    claim = subparsers.add_parser("claim", help="Claim operations.")
    claim_sub = claim.add_subparsers(dest="claim_command", required=True)

    evaluate = claim_sub.add_parser("evaluate", help="Evaluate one claim or all claims.")
    evaluate.add_argument("path", nargs="?", default=".", help="Registry file path or repository root.")
    evaluate.add_argument("--claim-id", default=None, help="Claim id to evaluate. Omit to evaluate all claims.")
    evaluate.set_defaults(func=run_evaluate)


def run_evaluate(args: argparse.Namespace) -> dict[str, object]:
    return evaluate_claims(path=args.path, claim_id=args.claim_id)
