from __future__ import annotations

from typing import Final

LEASE_PROVISIONING: Final = "provisioning"
LEASE_ACTIVE: Final = "active"
LEASE_DONE: Final = "done"
LEASE_BLOCKED: Final = "blocked"
LEASE_ABANDONED: Final = "abandoned"
LEASE_EXPIRED: Final = "expired"
LEASE_FAILED: Final = "failed"

OPEN_LEASE_STATUSES: Final = {LEASE_PROVISIONING, LEASE_ACTIVE}
TERMINAL_LEASE_STATUSES: Final = {
    LEASE_DONE,
    LEASE_BLOCKED,
    LEASE_ABANDONED,
    LEASE_EXPIRED,
    LEASE_FAILED,
}

EVENT_INFO: Final = "info"
EVENT_WARN: Final = "warn"
EVENT_ERROR: Final = "error"
EVENT_CRITICAL: Final = "critical"

WORK_MAY_BE_AVAILABLE: Final = "work_may_be_available"
REFRESH_CONTEXT: Final = "refresh_context"
PAUSE_AND_CHECK_CONFLICTS: Final = "pause_and_check_conflicts"
STOP_CURRENT_WORK: Final = "stop_current_work"
RENEW_LEASE: Final = "renew_lease"
NO_ACTION: Final = "none"

FORBIDDEN_EXACT_PATHS: Final = {
    ".ssot/registry.json",
    ".ssot/registry.json.lock",
}

FORBIDDEN_PATH_PREFIXES: Final = (
    ".git/",
    ".ssot/control/",
)
