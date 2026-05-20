from __future__ import annotations

import argparse
from pathlib import Path

from ssot_registry.control.service import ControlPlane


def register_leases(subparsers: argparse._SubParsersAction) -> None:
    leases = subparsers.add_parser("leases", help="Inspect and maintain worker path and maturation leases.")
    leases_sub = leases.add_subparsers(dest="leases_command", required=True)

    list_cmd = leases_sub.add_parser("list", help="List control-plane leases.")
    list_cmd.add_argument("path", nargs="?", default=".")
    list_cmd.add_argument("--status", default=None)
    list_cmd.set_defaults(func=run_list)

    inspect = leases_sub.add_parser("inspect", help="Inspect one control-plane lease.")
    inspect.add_argument("path", nargs="?", default=".")
    inspect.add_argument("--lease-id", required=True)
    inspect.set_defaults(func=run_inspect)

    expire = leases_sub.add_parser("expire", help="Expire due active leases and emit lease-expired events.")
    expire.add_argument("path", nargs="?", default=".")
    expire.set_defaults(func=run_expire)


def run_list(args: argparse.Namespace) -> dict[str, object]:
    plane = ControlPlane(Path(args.path))
    return {"passed": True, "leases": plane.store.list_leases(status=args.status)}


def run_inspect(args: argparse.Namespace) -> dict[str, object]:
    plane = ControlPlane(Path(args.path))
    lease = plane.store.get_lease(args.lease_id)
    if lease is None:
        raise ValueError(f"unknown lease: {args.lease_id}")
    return {"passed": True, "lease": lease}


def run_expire(args: argparse.Namespace) -> dict[str, object]:
    plane = ControlPlane(Path(args.path))
    return plane.expire_due_leases()
