from __future__ import annotations

import json
import os
import tempfile
import time
import uuid
from contextlib import AbstractContextManager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ssot_registry.util.errors import RegistryLockError
from ssot_registry.util.jsonio import stable_json_dumps

DEFAULT_REGISTRY_LOCK_TTL_SECONDS = 300


def _utc_epoch_seconds() -> float:
    return time.time()


def registry_lock_path(registry_path: str | Path) -> Path:
    return Path(registry_path).with_name(f"{Path(registry_path).name}.lock")


def _read_lock_metadata(lock_path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _is_stale(lock_path: Path, now: float) -> bool:
    metadata = _read_lock_metadata(lock_path)
    expires_at = metadata.get("expires_at_epoch")
    if isinstance(expires_at, int | float):
        return float(expires_at) <= now
    try:
        stat = lock_path.stat()
    except OSError:
        return False
    return stat.st_mtime + DEFAULT_REGISTRY_LOCK_TTL_SECONDS <= now


@dataclass
class RegistryFileLock(AbstractContextManager["RegistryFileLock"]):
    registry_path: Path
    reason: str = "registry mutation"
    ttl_seconds: int = DEFAULT_REGISTRY_LOCK_TTL_SECONDS
    owner: str | None = None

    def __post_init__(self) -> None:
        self.registry_path = Path(self.registry_path)
        self.lock_path = registry_lock_path(self.registry_path)
        self.token = uuid.uuid4().hex
        self.owner = self.owner or f"pid:{os.getpid()}"
        self._acquired = False

    def __enter__(self) -> "RegistryFileLock":
        self.acquire()
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.release()

    def acquire(self) -> None:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        now = _utc_epoch_seconds()
        metadata = {
            "target": self.registry_path.as_posix(),
            "owner": self.owner,
            "pid": os.getpid(),
            "reason": self.reason,
            "token": self.token,
            "created_at_epoch": now,
            "expires_at_epoch": now + self.ttl_seconds,
        }
        payload = stable_json_dumps(metadata)
        while True:
            try:
                fd = os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError as exc:
                if _is_stale(self.lock_path, _utc_epoch_seconds()):
                    try:
                        self.lock_path.unlink()
                    except FileNotFoundError:
                        continue
                    except OSError as unlink_error:
                        raise RegistryLockError(f"Failed to remove stale registry lock {self.lock_path}: {unlink_error}") from unlink_error
                    continue
                holder = _read_lock_metadata(self.lock_path)
                owner = holder.get("owner", "unknown")
                reason = holder.get("reason", "unknown")
                raise RegistryLockError(f"Registry is locked by {owner} for {reason}: {self.lock_path}") from exc
            with os.fdopen(fd, "w", encoding="utf-8") as lock_file:
                lock_file.write(payload)
                lock_file.flush()
                os.fsync(lock_file.fileno())
            self._acquired = True
            return

    def release(self) -> None:
        if not self._acquired:
            return
        metadata = _read_lock_metadata(self.lock_path)
        if metadata.get("token") != self.token:
            raise RegistryLockError(f"Registry lock owner mismatch; refusing to release {self.lock_path}")
        try:
            self.lock_path.unlink()
        except FileNotFoundError:
            pass
        self._acquired = False


def save_registry_json_locked(registry_path: str | Path, registry: dict[str, object], *, reason: str = "registry mutation") -> None:
    target = Path(registry_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with RegistryFileLock(target, reason=reason):
        payload = stable_json_dumps(registry)
        temp_name: str | None = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=target.parent, prefix=f".{target.name}.", suffix=".tmp", delete=False) as temp_file:
                temp_name = temp_file.name
                temp_file.write(payload)
                temp_file.flush()
                os.fsync(temp_file.fileno())
            os.replace(temp_name, target)
        finally:
            if temp_name is not None:
                temp_path = Path(temp_name)
                if temp_path.exists():
                    try:
                        temp_path.unlink()
                    except OSError:
                        pass
