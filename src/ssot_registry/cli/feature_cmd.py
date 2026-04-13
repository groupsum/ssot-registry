from __future__ import annotations

import argparse

from ssot_registry.api import plan_features, set_feature_lifecycle


def register_feature(subparsers: argparse._SubParsersAction) -> None:
    feature = subparsers.add_parser("feature", help="Feature operations.")
    feature_sub = feature.add_subparsers(dest="feature_command", required=True)

    plan = feature_sub.add_parser("plan", help="Plan feature horizons, tiers, and target lifecycle.")
    plan.add_argument("path", nargs="?", default=".", help="Registry file path or repository root.")
    plan.add_argument("--ids", nargs="+", required=True, help="Feature ids to update.")
    plan.add_argument(
        "--horizon",
        required=True,
        choices=["current", "next", "future", "explicit", "backlog", "out_of_bounds"],
        help="Planning horizon.",
    )
    plan.add_argument("--claim-tier", choices=["T0", "T1", "T2", "T3", "T4"], default=None, help="Target claim tier.")
    plan.add_argument(
        "--target-lifecycle-stage",
        choices=["active", "deprecated", "obsolete", "removed"],
        default=None,
        help="Planned lifecycle target for the feature.",
    )
    plan.add_argument("--slot", default=None, help="Explicit slot or label when horizon is explicit.")
    plan.set_defaults(func=run_plan)

    lifecycle = feature_sub.add_parser("lifecycle", help="Feature lifecycle operations.")
    lifecycle_sub = lifecycle.add_subparsers(dest="feature_lifecycle_command", required=True)
    lifecycle_set = lifecycle_sub.add_parser("set", help="Set actual feature lifecycle state.")
    lifecycle_set.add_argument("path", nargs="?", default=".", help="Registry file path or repository root.")
    lifecycle_set.add_argument("--ids", nargs="+", required=True, help="Feature ids to update.")
    lifecycle_set.add_argument("--stage", required=True, choices=["active", "deprecated", "obsolete", "removed"])
    lifecycle_set.add_argument("--replacement-feature-id", nargs="*", default=None, help="Replacement feature id(s).")
    lifecycle_set.add_argument("--effective-release-id", default=None, help="Effective release id.")
    lifecycle_set.add_argument("--note", default=None, help="Lifecycle note or rationale.")
    lifecycle_set.set_defaults(func=run_lifecycle_set)


def run_plan(args: argparse.Namespace) -> dict[str, object]:
    return plan_features(
        path=args.path,
        ids=args.ids,
        horizon=args.horizon,
        claim_tier=args.claim_tier,
        slot=args.slot,
        target_lifecycle_stage=args.target_lifecycle_stage,
    )


def run_lifecycle_set(args: argparse.Namespace) -> dict[str, object]:
    return set_feature_lifecycle(
        path=args.path,
        ids=args.ids,
        stage=args.stage,
        replacement_feature_ids=args.replacement_feature_id,
        note=args.note,
        effective_release_id=args.effective_release_id,
    )
