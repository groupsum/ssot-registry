from __future__ import annotations

import argparse
from pathlib import Path

from ssot_registry.control.service import ControlPlane


def register_worker(subparsers: argparse._SubParsersAction) -> None:
    worker = subparsers.add_parser("worker", help="Operate pull-worker control-plane actions.")
    worker_sub = worker.add_subparsers(dest="worker_command", required=True)

    register = worker_sub.add_parser("register", help="Register or heartbeat a worker identity.")
    register.add_argument("path", nargs="?", default=".")
    register.add_argument("--worker-id", required=True)
    register.add_argument("--os-user", default=None)
    register.set_defaults(func=run_register)

    claim = worker_sub.add_parser("claim-next", help="Pull the next maturation slice and create a lease.")
    claim.add_argument("path", nargs="?", default=".")
    claim.add_argument("--worker-id", required=True)
    claim.add_argument("--campaign-id", required=True)
    claim.add_argument("--target-tier", default="T2", choices=["T0", "T1", "T2", "T3", "T4"])
    claim.add_argument("--os-user", default=None)
    claim.add_argument("--ttl-seconds", type=int, default=1800)
    claim.add_argument("--feature-ids", nargs="*", default=None)
    claim.add_argument("--profile-ids", nargs="*", default=None)
    claim.add_argument("--boundary-ids", nargs="*", default=None)
    claim.add_argument("--max-blockers-per-claim", type=int, default=5)
    claim.add_argument("--feature-limit", type=int, default=25, help="Maximum in-bounds features to consider for this claim. Defaults to 25.")
    claim.add_argument(
        "--auto-scaffold",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Automatically scaffold missing target-tier claim/test/evidence wiring before blocking. Enabled by default.",
    )
    claim.set_defaults(func=run_claim_next)

    renew = worker_sub.add_parser("renew", help="Renew an active lease.")
    renew.add_argument("path", nargs="?", default=".")
    renew.add_argument("--worker-id", required=True)
    renew.add_argument("--lease-id", required=True)
    renew.add_argument("--fencing-token", required=True, type=int)
    renew.add_argument("--ttl-seconds", type=int, default=1800)
    renew.set_defaults(func=run_renew)

    abandon = worker_sub.add_parser("abandon", help="Abandon an active lease.")
    abandon.add_argument("path", nargs="?", default=".")
    abandon.add_argument("--worker-id", required=True)
    abandon.add_argument("--lease-id", required=True)
    abandon.add_argument("--fencing-token", required=True, type=int)
    abandon.add_argument("--reason", required=True)
    abandon.set_defaults(func=run_abandon)

    events = worker_sub.add_parser("events", help="Poll durable worker events.")
    events.add_argument("path", nargs="?", default=".")
    events.add_argument("--worker-id", default=None)
    events.add_argument("--campaign-id", default=None)
    events.add_argument("--after-event-id", type=int, default=0)
    events.add_argument("--limit", type=int, default=100)
    events.set_defaults(func=run_events)

    ack = worker_sub.add_parser("ack-events", help="ACK durable worker events.")
    ack.add_argument("path", nargs="?", default=".")
    ack.add_argument("--worker-id", required=True)
    ack.add_argument("--event-ids", nargs="+", required=True, type=int)
    ack.add_argument("--action", default="processed")
    ack.set_defaults(func=run_ack)


def run_register(args: argparse.Namespace) -> dict[str, object]:
    return ControlPlane(Path(args.path)).register_worker(args.worker_id, os_user=args.os_user)


def run_claim_next(args: argparse.Namespace) -> dict[str, object]:
    return ControlPlane(Path(args.path)).claim_next_maturation_slice(
        worker_id=args.worker_id,
        campaign_id=args.campaign_id,
        target_tier=args.target_tier,
        os_user=args.os_user,
        ttl_seconds=args.ttl_seconds,
        feature_ids=args.feature_ids,
        profile_ids=args.profile_ids,
        boundary_ids=args.boundary_ids,
        max_blockers_per_claim=args.max_blockers_per_claim,
        auto_scaffold=args.auto_scaffold,
        feature_limit=args.feature_limit,
    )


def run_renew(args: argparse.Namespace) -> dict[str, object]:
    return ControlPlane(Path(args.path)).renew_lease(
        worker_id=args.worker_id,
        lease_id=args.lease_id,
        fencing_token=args.fencing_token,
        ttl_seconds=args.ttl_seconds,
    )


def run_abandon(args: argparse.Namespace) -> dict[str, object]:
    return ControlPlane(Path(args.path)).abandon_slice(
        worker_id=args.worker_id,
        lease_id=args.lease_id,
        fencing_token=args.fencing_token,
        reason=args.reason,
    )


def run_events(args: argparse.Namespace) -> dict[str, object]:
    return ControlPlane(Path(args.path)).get_worker_events(
        worker_id=args.worker_id,
        campaign_id=args.campaign_id,
        after_event_id=args.after_event_id,
        limit=args.limit,
    )


def run_ack(args: argparse.Namespace) -> dict[str, object]:
    return ControlPlane(Path(args.path)).ack_worker_events(
        worker_id=args.worker_id,
        event_ids=args.event_ids,
        action=args.action,
    )
