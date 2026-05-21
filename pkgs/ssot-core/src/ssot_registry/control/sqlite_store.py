from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4

from ssot_registry.util.time import utc_now_iso

from .models import (
    EVENT_ERROR,
    EVENT_INFO,
    LEASE_ABANDONED,
    LEASE_ACTIVE,
    LEASE_DONE,
    LEASE_EXPIRED,
    LEASE_FAILED,
    LEASE_PROVISIONING,
    OPEN_LEASE_STATUSES,
    TERMINAL_LEASE_STATUSES,
    NO_ACTION,
)
from .paths import ensure_allowed_path, path_overlaps


def control_db_path(repo_root: str | Path) -> Path:
    return Path(repo_root) / ".ssot" / "control" / "state.sqlite"


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _json_loads(value: str | None) -> Any:
    if not value:
        return None
    return json.loads(value)


def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    result = dict(row)
    for key in ("metadata_json", "payload_json", "result_json", "changed_paths_json", "failures_json", "warnings_json", "checks_json"):
        if key in result:
            result[key.removesuffix("_json")] = _json_loads(result.pop(key))
    return result


class ControlStore:
    """SQLite-backed durable control state for optional worker orchestration."""

    def __init__(self, repo_root: str | Path, db_path: str | Path | None = None) -> None:
        self.repo_root = Path(repo_root)
        self.db_path = Path(db_path) if db_path is not None else control_db_path(self.repo_root)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS workers (
                    worker_id TEXT PRIMARY KEY,
                    os_user TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    heartbeat_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS campaigns (
                    campaign_id TEXT PRIMARY KEY,
                    target_tier TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    metadata_json TEXT NOT NULL DEFAULT '{}'
                );

                CREATE TABLE IF NOT EXISTS maturation_leases (
                    lease_id TEXT PRIMARY KEY,
                    campaign_id TEXT NOT NULL,
                    worker_id TEXT NOT NULL,
                    feature_id TEXT NOT NULL,
                    from_tier TEXT NOT NULL,
                    to_tier TEXT NOT NULL,
                    status TEXT NOT NULL,
                    fencing_token INTEGER NOT NULL,
                    registry_hash_at_claim TEXT NOT NULL,
                    git_head_at_claim TEXT,
                    created_at TEXT NOT NULL,
                    heartbeat_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    completed_at TEXT,
                    result_json TEXT NOT NULL DEFAULT '{}'
                );

                CREATE UNIQUE INDEX IF NOT EXISTS idx_maturation_open_transition
                ON maturation_leases(feature_id, from_tier, to_tier)
                WHERE status IN ('provisioning', 'active');

                CREATE TABLE IF NOT EXISTS path_leases (
                    path_lease_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lease_id TEXT NOT NULL,
                    path TEXT NOT NULL,
                    access TEXT NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY (lease_id) REFERENCES maturation_leases(lease_id)
                );

                CREATE INDEX IF NOT EXISTS idx_path_leases_status_path
                ON path_leases(status, path);

                CREATE TABLE IF NOT EXISTS worker_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL,
                    campaign_id TEXT,
                    worker_id TEXT,
                    lease_id TEXT,
                    severity TEXT NOT NULL,
                    recommended_action TEXT NOT NULL,
                    payload_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS worker_event_acks (
                    worker_id TEXT NOT NULL,
                    event_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    acked_at TEXT NOT NULL,
                    PRIMARY KEY(worker_id, event_id)
                );

                CREATE TABLE IF NOT EXISTS conflicts (
                    conflict_id TEXT PRIMARY KEY,
                    campaign_id TEXT,
                    owner_lease_id TEXT,
                    owner_worker_id TEXT,
                    suspected_actor TEXT,
                    changed_paths_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS blocked_transitions (
                    blocked_id TEXT PRIMARY KEY,
                    campaign_id TEXT NOT NULL,
                    feature_id TEXT NOT NULL,
                    from_tier TEXT NOT NULL,
                    to_tier TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    status TEXT NOT NULL,
                    failures_json TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE UNIQUE INDEX IF NOT EXISTS idx_blocked_transition_open
                ON blocked_transitions(campaign_id, feature_id, from_tier, to_tier)
                WHERE status = 'open';

                CREATE TABLE IF NOT EXISTS tier_gate_reports (
                    report_id TEXT PRIMARY KEY,
                    lease_id TEXT,
                    feature_id TEXT NOT NULL,
                    requested_tier TEXT NOT NULL,
                    approved_tier TEXT NOT NULL,
                    passed INTEGER NOT NULL,
                    failures_json TEXT NOT NULL,
                    warnings_json TEXT NOT NULL,
                    checks_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def register_worker(self, worker_id: str, os_user: str | None = None, status: str = "active") -> dict[str, Any]:
        self.initialize()
        now = utc_now_iso()
        user = os_user or worker_id
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO workers(worker_id, os_user, status, started_at, heartbeat_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(worker_id) DO UPDATE SET
                    os_user = excluded.os_user,
                    status = excluded.status,
                    heartbeat_at = excluded.heartbeat_at
                """,
                (worker_id, user, status, now, now),
            )
            return dict(conn.execute("SELECT * FROM workers WHERE worker_id = ?", (worker_id,)).fetchone())

    def ensure_campaign(self, campaign_id: str, target_tier: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        self.initialize()
        now = utc_now_iso()
        metadata_payload = metadata or {}
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO campaigns(campaign_id, target_tier, status, created_at, metadata_json)
                VALUES (?, ?, 'active', ?, ?)
                ON CONFLICT(campaign_id) DO UPDATE SET
                    metadata_json = CASE
                        WHEN excluded.metadata_json = '{}' THEN campaigns.metadata_json
                        ELSE excluded.metadata_json
                    END
                """,
                (campaign_id, target_tier, now, _json_dumps(metadata_payload)),
            )
            return _row_to_dict(conn.execute("SELECT * FROM campaigns WHERE campaign_id = ?", (campaign_id,)).fetchone()) or {}

    def active_path_leases(self) -> list[dict[str, Any]]:
        self.initialize()
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT p.*, m.worker_id, m.campaign_id, m.feature_id
                FROM path_leases p
                JOIN maturation_leases m ON m.lease_id = p.lease_id
                WHERE p.status = ? AND m.status = ?
                ORDER BY p.path
                """,
                (LEASE_ACTIVE, LEASE_ACTIVE),
            ).fetchall()
            return [dict(row) for row in rows]

    def assert_no_path_conflicts(self, paths: list[str]) -> None:
        active = self.active_path_leases()
        for path in paths:
            rel = ensure_allowed_path(path)
            for lease in active:
                if path_overlaps(rel, lease["path"]):
                    raise ValueError(f"path lease conflict: {rel} overlaps active lease {lease['lease_id']}:{lease['path']}")

    def create_maturation_lease(
        self,
        *,
        campaign_id: str,
        worker_id: str,
        feature_id: str,
        from_tier: str,
        to_tier: str,
        path_roots: list[str],
        registry_hash_at_claim: str,
        expires_at: str,
        git_head_at_claim: str | None = None,
    ) -> dict[str, Any]:
        self.initialize()
        normalized_roots = [ensure_allowed_path(path) for path in path_roots]
        self.assert_no_path_conflicts(normalized_roots)
        lease_id = f"lease:{uuid4().hex}"
        now = utc_now_iso()
        with self.connect() as conn:
            max_token = conn.execute("SELECT COALESCE(MAX(fencing_token), 0) FROM maturation_leases").fetchone()[0]
            fencing_token = int(max_token) + 1
            conn.execute(
                """
                INSERT INTO maturation_leases(
                    lease_id, campaign_id, worker_id, feature_id, from_tier, to_tier,
                    status, fencing_token, registry_hash_at_claim, git_head_at_claim,
                    created_at, heartbeat_at, expires_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    lease_id,
                    campaign_id,
                    worker_id,
                    feature_id,
                    from_tier,
                    to_tier,
                    LEASE_PROVISIONING,
                    fencing_token,
                    registry_hash_at_claim,
                    git_head_at_claim,
                    now,
                    now,
                    expires_at,
                ),
            )
            for root in normalized_roots:
                conn.execute(
                    "INSERT INTO path_leases(lease_id, path, access, status) VALUES (?, ?, 'write', ?)",
                    (lease_id, root, LEASE_PROVISIONING),
                )
            return self.get_lease(lease_id, conn=conn) or {}

    def activate_lease(self, lease_id: str) -> dict[str, Any]:
        now = utc_now_iso()
        with self.connect() as conn:
            conn.execute(
                "UPDATE maturation_leases SET status = ?, heartbeat_at = ? WHERE lease_id = ? AND status = ?",
                (LEASE_ACTIVE, now, lease_id, LEASE_PROVISIONING),
            )
            conn.execute("UPDATE path_leases SET status = ? WHERE lease_id = ?", (LEASE_ACTIVE, lease_id))
            return self.get_lease(lease_id, conn=conn) or {}

    def mark_lease_failed(self, lease_id: str, reason: str) -> dict[str, Any]:
        return self._finish_lease(lease_id, LEASE_FAILED, {"reason": reason})

    def renew_lease(self, lease_id: str, worker_id: str, fencing_token: int, expires_at: str) -> dict[str, Any]:
        now = utc_now_iso()
        with self.connect() as conn:
            lease = self.get_lease(lease_id, conn=conn)
            self._assert_active_lease(lease, worker_id, fencing_token)
            conn.execute(
                "UPDATE maturation_leases SET heartbeat_at = ?, expires_at = ? WHERE lease_id = ?",
                (now, expires_at, lease_id),
            )
            return self.get_lease(lease_id, conn=conn) or {}

    def complete_lease(self, lease_id: str, worker_id: str, fencing_token: int, result: dict[str, Any]) -> dict[str, Any]:
        with self.connect() as conn:
            lease = self.get_lease(lease_id, conn=conn)
            self._assert_active_lease(lease, worker_id, fencing_token)
        return self._finish_lease(lease_id, LEASE_DONE, result)

    def abandon_lease(self, lease_id: str, worker_id: str, fencing_token: int, reason: str) -> dict[str, Any]:
        with self.connect() as conn:
            lease = self.get_lease(lease_id, conn=conn)
            self._assert_active_lease(lease, worker_id, fencing_token)
        return self._finish_lease(lease_id, LEASE_ABANDONED, {"reason": reason})

    def expire_due_leases(self, now_iso: str | None = None) -> list[dict[str, Any]]:
        cutoff = now_iso or utc_now_iso()
        expired: list[dict[str, Any]] = []
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT lease_id FROM maturation_leases WHERE status = ? AND expires_at <= ? ORDER BY expires_at",
                (LEASE_ACTIVE, cutoff),
            ).fetchall()
        for row in rows:
            expired.append(self._finish_lease(row["lease_id"], LEASE_EXPIRED, {"reason": "ttl_expired"}))
        return expired

    def _finish_lease(self, lease_id: str, status: str, result: dict[str, Any]) -> dict[str, Any]:
        if status not in TERMINAL_LEASE_STATUSES:
            raise ValueError(f"unsupported terminal lease status: {status}")
        now = utc_now_iso()
        with self.connect() as conn:
            conn.execute(
                "UPDATE maturation_leases SET status = ?, completed_at = ?, result_json = ? WHERE lease_id = ?",
                (status, now, _json_dumps(result), lease_id),
            )
            conn.execute("UPDATE path_leases SET status = ? WHERE lease_id = ?", (status, lease_id))
            return self.get_lease(lease_id, conn=conn) or {}

    def _assert_active_lease(self, lease: dict[str, Any] | None, worker_id: str, fencing_token: int) -> None:
        if lease is None:
            raise ValueError("unknown lease")
        if lease["status"] != LEASE_ACTIVE:
            raise ValueError(f"lease is not active: {lease['status']}")
        if lease["worker_id"] != worker_id:
            raise ValueError("worker does not own lease")
        if int(lease["fencing_token"]) != int(fencing_token):
            raise ValueError("stale fencing token")

    def get_lease(self, lease_id: str, *, conn: sqlite3.Connection | None = None) -> dict[str, Any] | None:
        close_conn = False
        if conn is None:
            self.initialize()
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            close_conn = True
        try:
            lease = _row_to_dict(conn.execute("SELECT * FROM maturation_leases WHERE lease_id = ?", (lease_id,)).fetchone())
            if lease is None:
                return None
            path_rows = conn.execute("SELECT path, access, status FROM path_leases WHERE lease_id = ? ORDER BY path", (lease_id,)).fetchall()
            lease["path_leases"] = [dict(row) for row in path_rows]
            lease["path_roots"] = [row["path"] for row in path_rows]
            return lease
        finally:
            if close_conn:
                conn.close()

    def list_leases(self, status: str | None = None) -> list[dict[str, Any]]:
        self.initialize()
        with self.connect() as conn:
            if status is None:
                rows = conn.execute("SELECT lease_id FROM maturation_leases ORDER BY created_at, lease_id").fetchall()
            else:
                rows = conn.execute("SELECT lease_id FROM maturation_leases WHERE status = ? ORDER BY created_at, lease_id", (status,)).fetchall()
            return [self.get_lease(row["lease_id"], conn=conn) or {} for row in rows]

    def emit_event(
        self,
        kind: str,
        *,
        campaign_id: str | None = None,
        worker_id: str | None = None,
        lease_id: str | None = None,
        severity: str = EVENT_INFO,
        recommended_action: str = NO_ACTION,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.initialize()
        now = utc_now_iso()
        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO worker_events(kind, campaign_id, worker_id, lease_id, severity, recommended_action, payload_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (kind, campaign_id, worker_id, lease_id, severity, recommended_action, _json_dumps(payload or {}), now),
            )
            event_id = int(cursor.lastrowid)
            return self.get_event(event_id, conn=conn) or {}

    def get_event(self, event_id: int, *, conn: sqlite3.Connection | None = None) -> dict[str, Any] | None:
        close_conn = False
        if conn is None:
            self.initialize()
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            close_conn = True
        try:
            return _row_to_dict(conn.execute("SELECT * FROM worker_events WHERE event_id = ?", (event_id,)).fetchone())
        finally:
            if close_conn:
                conn.close()

    def get_events(
        self,
        *,
        worker_id: str | None = None,
        campaign_id: str | None = None,
        after_event_id: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        self.initialize()
        clauses = ["event_id > ?"]
        params: list[Any] = [after_event_id]
        if campaign_id is not None:
            clauses.append("(campaign_id IS NULL OR campaign_id = ?)")
            params.append(campaign_id)
        if worker_id is not None:
            clauses.append("(worker_id IS NULL OR worker_id = ?)")
            params.append(worker_id)
        params.append(limit)
        with self.connect() as conn:
            rows = conn.execute(
                f"SELECT * FROM worker_events WHERE {' AND '.join(clauses)} ORDER BY event_id LIMIT ?",
                params,
            ).fetchall()
            return [_row_to_dict(row) or {} for row in rows]

    def ack_events(self, worker_id: str, event_ids: list[int], action: str) -> dict[str, Any]:
        self.initialize()
        now = utc_now_iso()
        with self.connect() as conn:
            for event_id in event_ids:
                conn.execute(
                    """
                    INSERT INTO worker_event_acks(worker_id, event_id, action, acked_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(worker_id, event_id) DO UPDATE SET
                        action = excluded.action,
                        acked_at = excluded.acked_at
                    """,
                    (worker_id, int(event_id), action, now),
                )
        return {"passed": True, "worker_id": worker_id, "acked_event_ids": sorted(set(event_ids)), "action": action}

    def create_conflict(
        self,
        *,
        campaign_id: str | None,
        owner_lease_id: str | None,
        owner_worker_id: str | None,
        suspected_actor: str | None,
        changed_paths: list[str],
    ) -> dict[str, Any]:
        self.initialize()
        conflict_id = f"cnf:{uuid4().hex}"
        now = utc_now_iso()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO conflicts(conflict_id, campaign_id, owner_lease_id, owner_worker_id, suspected_actor, changed_paths_json, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'open', ?)
                """,
                (conflict_id, campaign_id, owner_lease_id, owner_worker_id, suspected_actor, _json_dumps(changed_paths), now),
            )
            conflict = _row_to_dict(conn.execute("SELECT * FROM conflicts WHERE conflict_id = ?", (conflict_id,)).fetchone()) or {}
        self.emit_event(
            "path_conflict_detected",
            campaign_id=campaign_id,
            lease_id=owner_lease_id,
            severity=EVENT_ERROR,
            recommended_action="pause_and_check_conflicts",
            payload=conflict,
        )
        return conflict

    def get_conflicts(self, status: str | None = "open") -> list[dict[str, Any]]:
        self.initialize()
        with self.connect() as conn:
            if status is None:
                rows = conn.execute("SELECT * FROM conflicts ORDER BY created_at").fetchall()
            else:
                rows = conn.execute("SELECT * FROM conflicts WHERE status = ? ORDER BY created_at", (status,)).fetchall()
            return [_row_to_dict(row) or {} for row in rows]

    def record_blocked_transition(
        self,
        *,
        campaign_id: str,
        feature_id: str,
        from_tier: str,
        to_tier: str,
        reason: str,
        failures: list[str],
    ) -> dict[str, Any]:
        self.initialize()
        blocked_id = f"blk:{uuid4().hex}"
        now = utc_now_iso()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO blocked_transitions(
                    blocked_id, campaign_id, feature_id, from_tier, to_tier, reason,
                    status, failures_json, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, 'open', ?, ?, ?)
                ON CONFLICT(campaign_id, feature_id, from_tier, to_tier)
                WHERE status = 'open'
                DO UPDATE SET
                    reason = excluded.reason,
                    failures_json = excluded.failures_json,
                    updated_at = excluded.updated_at
                """,
                (blocked_id, campaign_id, feature_id, from_tier, to_tier, reason, _json_dumps(failures), now, now),
            )
            row = conn.execute(
                """
                SELECT * FROM blocked_transitions
                WHERE campaign_id = ? AND feature_id = ? AND from_tier = ? AND to_tier = ? AND status = 'open'
                """,
                (campaign_id, feature_id, from_tier, to_tier),
            ).fetchone()
            return _row_to_dict(row) or {}

    def get_blocked_transitions(self, campaign_id: str | None = None, status: str | None = "open") -> list[dict[str, Any]]:
        self.initialize()
        clauses: list[str] = []
        params: list[Any] = []
        if campaign_id is not None:
            clauses.append("campaign_id = ?")
            params.append(campaign_id)
        if status is not None:
            clauses.append("status = ?")
            params.append(status)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.connect() as conn:
            rows = conn.execute(f"SELECT * FROM blocked_transitions {where} ORDER BY updated_at, blocked_id", params).fetchall()
            return [_row_to_dict(row) or {} for row in rows]

    def get_blocked_transition(self, blocked_id: str, *, conn: sqlite3.Connection | None = None) -> dict[str, Any] | None:
        close_conn = False
        if conn is None:
            self.initialize()
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            close_conn = True
        try:
            row = conn.execute("SELECT * FROM blocked_transitions WHERE blocked_id = ?", (blocked_id,)).fetchone()
            return _row_to_dict(row)
        finally:
            if close_conn:
                conn.close()

    def resolve_blocked_transition(self, blocked_id: str, reason: str = "repaired") -> dict[str, Any]:
        self.initialize()
        now = utc_now_iso()
        with self.connect() as conn:
            conn.execute(
                "UPDATE blocked_transitions SET status = 'resolved', reason = ?, updated_at = ? WHERE blocked_id = ?",
                (reason, now, blocked_id),
            )
            row = conn.execute("SELECT * FROM blocked_transitions WHERE blocked_id = ?", (blocked_id,)).fetchone()
            return _row_to_dict(row) or {}

    def resolve_matching_blocked_transitions(
        self,
        *,
        feature_id: str,
        to_tier: str | None = None,
        reason: str = "repaired",
        campaign_id: str | None = None,
    ) -> list[dict[str, Any]]:
        self.initialize()
        now = utc_now_iso()
        clauses = ["feature_id = ?", "status = 'open'"]
        params: list[Any] = [feature_id]
        if to_tier is not None:
            clauses.append("to_tier = ?")
            params.append(to_tier)
        if campaign_id is not None:
            clauses.append("campaign_id = ?")
            params.append(campaign_id)
        where = " AND ".join(clauses)
        select_clauses = ["feature_id = ?", "status = 'resolved'"]
        select_params: list[Any] = [feature_id]
        if to_tier is not None:
            select_clauses.append("to_tier = ?")
            select_params.append(to_tier)
        if campaign_id is not None:
            select_clauses.append("campaign_id = ?")
            select_params.append(campaign_id)
        with self.connect() as conn:
            conn.execute(
                f"UPDATE blocked_transitions SET status = 'resolved', reason = ?, updated_at = ? WHERE {where}",
                (reason, now, *params),
            )
            rows = conn.execute(
                f"SELECT * FROM blocked_transitions WHERE {' AND '.join(select_clauses)} ORDER BY updated_at, blocked_id",
                select_params,
            ).fetchall()
            return [_row_to_dict(row) or {} for row in rows]

    def record_gate_report(
        self,
        *,
        lease_id: str | None,
        feature_id: str,
        gate_result: dict[str, Any],
    ) -> dict[str, Any]:
        self.initialize()
        report_id = f"gtr:{uuid4().hex}"
        now = utc_now_iso()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO tier_gate_reports(
                    report_id, lease_id, feature_id, requested_tier, approved_tier, passed,
                    failures_json, warnings_json, checks_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    report_id,
                    lease_id,
                    feature_id,
                    gate_result.get("requested_tier", "T0"),
                    gate_result.get("approved_tier", "T0"),
                    1 if gate_result.get("passed") else 0,
                    _json_dumps(gate_result.get("failures", [])),
                    _json_dumps(gate_result.get("warnings", [])),
                    _json_dumps(gate_result.get("checks", {})),
                    now,
                ),
            )
            return _row_to_dict(conn.execute("SELECT * FROM tier_gate_reports WHERE report_id = ?", (report_id,)).fetchone()) or {}

    def campaign_status(self, campaign_id: str) -> dict[str, Any]:
        self.initialize()
        with self.connect() as conn:
            campaign = _row_to_dict(conn.execute("SELECT * FROM campaigns WHERE campaign_id = ?", (campaign_id,)).fetchone())
            lease_rows = conn.execute(
                "SELECT status, COUNT(*) AS count FROM maturation_leases WHERE campaign_id = ? GROUP BY status",
                (campaign_id,),
            ).fetchall()
            blocked_count = conn.execute(
                "SELECT COUNT(*) FROM blocked_transitions WHERE campaign_id = ? AND status = 'open'",
                (campaign_id,),
            ).fetchone()[0]
            counts = {row["status"]: row["count"] for row in lease_rows}
            active = sum(counts.get(status, 0) for status in OPEN_LEASE_STATUSES)
            return {
                "campaign_id": campaign_id,
                "campaign": campaign,
                "lease_counts": counts,
                "blocked_transition_count": int(blocked_count),
                "active_lease_count": active,
            }

    def mark_campaign_complete(self, campaign_id: str) -> dict[str, Any]:
        now = utc_now_iso()
        with self.connect() as conn:
            conn.execute(
                "UPDATE campaigns SET status = 'complete', completed_at = ? WHERE campaign_id = ?",
                (now, campaign_id),
            )
        self.emit_event("campaign_complete", campaign_id=campaign_id, recommended_action=NO_ACTION)
        return self.campaign_status(campaign_id)
