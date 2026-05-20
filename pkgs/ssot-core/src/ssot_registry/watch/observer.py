from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ssot_registry.control.models import EVENT_CRITICAL, EVENT_ERROR, PAUSE_AND_CHECK_CONFLICTS, REFRESH_CONTEXT, STOP_CURRENT_WORK
from ssot_registry.control.paths import is_forbidden_path, path_is_under
from ssot_registry.control.sqlite_store import ControlStore

from .git_status import git_changed_paths


@dataclass(frozen=True)
class RepoWatchScan:
    changed_paths: list[str]
    authorized_paths: list[str]
    out_of_lease_paths: list[str]
    forbidden_paths: list[str]
    conflicts: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "changed_paths": self.changed_paths,
            "authorized_paths": self.authorized_paths,
            "out_of_lease_paths": self.out_of_lease_paths,
            "forbidden_paths": self.forbidden_paths,
            "conflicts": self.conflicts,
        }


def classify_changed_paths(changed_paths: list[str], active_leases: list[dict[str, Any]]) -> RepoWatchScan:
    authorized: list[str] = []
    out_of_lease: list[str] = []
    forbidden: list[str] = []
    conflicts: list[dict[str, Any]] = []

    for path in changed_paths:
        if is_forbidden_path(path):
            forbidden.append(path)
            continue
        covering = [lease for lease in active_leases if path_is_under(path, lease["path"])]
        if covering:
            authorized.append(path)
        else:
            out_of_lease.append(path)

    for path in out_of_lease:
        owners = [lease for lease in active_leases if path_is_under(path, lease["path"])]
        for owner in owners:
            conflicts.append(
                {
                    "owner_lease_id": owner["lease_id"],
                    "owner_worker_id": owner.get("worker_id"),
                    "changed_paths": [path],
                }
            )

    return RepoWatchScan(
        changed_paths=sorted(dict.fromkeys(changed_paths)),
        authorized_paths=sorted(dict.fromkeys(authorized)),
        out_of_lease_paths=sorted(dict.fromkeys(out_of_lease)),
        forbidden_paths=sorted(dict.fromkeys(forbidden)),
        conflicts=conflicts,
    )


def scan_repo(repo_root: str | Path, store: ControlStore | None = None, *, emit_events: bool = True) -> dict[str, Any]:
    root = Path(repo_root)
    control_store = store or ControlStore(root)
    control_store.initialize()
    scan = classify_changed_paths(git_changed_paths(root), control_store.active_path_leases())
    if emit_events and scan.changed_paths:
        control_store.emit_event(
            "worktree_changed",
            severity="info",
            recommended_action=REFRESH_CONTEXT,
            payload=scan.as_dict(),
        )
    if emit_events and scan.out_of_lease_paths:
        control_store.emit_event(
            "out_of_lease_path_changed",
            severity=EVENT_ERROR,
            recommended_action=PAUSE_AND_CHECK_CONFLICTS,
            payload={"changed_paths": scan.out_of_lease_paths},
        )
    if emit_events and scan.forbidden_paths:
        kind = "unauthorized_registry_write" if ".ssot/registry.json" in scan.forbidden_paths else "forbidden_path_changed"
        control_store.emit_event(
            kind,
            severity=EVENT_CRITICAL,
            recommended_action=STOP_CURRENT_WORK,
            payload={"changed_paths": scan.forbidden_paths},
        )
    return {"passed": True, **scan.as_dict()}
