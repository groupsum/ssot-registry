from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from ssot_registry.api.save import save_registry, save_registry_unchecked
from ssot_registry.util.errors import RegistryLockError, ValidationError
from ssot_registry.util.jsonio import load_json, stable_json_dumps
from ssot_registry.util.registry_lock import RegistryFileLock, registry_lock_path, save_registry_json_locked
from tests.helpers import PROJECT_ROOT, temp_repo_from_fixture, workspace_tempdir


class RegistryFileLockTests(unittest.TestCase):
    def test_registry_file_lock_creates_and_removes_sidecar(self) -> None:
        with workspace_tempdir() as temp_dir:
            registry_path = Path(temp_dir) / ".ssot" / "registry.json"
            registry_path.parent.mkdir(parents=True)

            with RegistryFileLock(registry_path, reason="unit test"):
                self.assertTrue(registry_lock_path(registry_path).exists())

            self.assertFalse(registry_lock_path(registry_path).exists())

    def test_save_registry_rejects_active_competing_lock(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = load_json(registry_path)

        with RegistryFileLock(registry_path, reason="active owner"):
            with self.assertRaisesRegex(RegistryLockError, "Registry is locked"):
                save_registry(registry_path, registry)

    def test_save_registry_takes_over_stale_lock(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        lock_path = registry_lock_path(registry_path)
        lock_path.write_text(
            stable_json_dumps(
                {
                    "target": registry_path.as_posix(),
                    "owner": "stale-owner",
                    "reason": "expired test lock",
                    "token": "stale",
                    "created_at_epoch": 1,
                    "expires_at_epoch": 1,
                }
            ),
            encoding="utf-8",
        )

        save_registry(registry_path, load_json(registry_path))

        self.assertFalse(lock_path.exists())

    def test_save_registry_rejects_invalid_registry_before_write(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        original = load_json(registry_path)
        invalid = dict(original)
        invalid.pop("repo")

        with self.assertRaisesRegex(ValidationError, "Registry validation failed before saving registry"):
            save_registry(registry_path, invalid)

        self.assertEqual(load_json(registry_path), original)

    def test_save_registry_unchecked_is_explicit_lock_only_escape_hatch(self) -> None:
        with workspace_tempdir() as temp_dir:
            registry_path = Path(temp_dir) / ".ssot" / "registry.json"
            registry_path.parent.mkdir(parents=True)
            invalid = {"schema_version": "0.7.0"}

            save_registry_unchecked(registry_path, invalid)

            self.assertEqual(load_json(registry_path), invalid)

    def test_lock_release_refuses_non_owner_token(self) -> None:
        with workspace_tempdir() as temp_dir:
            registry_path = Path(temp_dir) / ".ssot" / "registry.json"
            registry_path.parent.mkdir(parents=True)
            lock = RegistryFileLock(registry_path)
            lock.acquire()
            self.addCleanup(lambda: registry_lock_path(registry_path).unlink(missing_ok=True))
            metadata = json.loads(registry_lock_path(registry_path).read_text(encoding="utf-8"))
            metadata["token"] = "other-owner"
            registry_lock_path(registry_path).write_text(stable_json_dumps(metadata), encoding="utf-8")

            with self.assertRaisesRegex(RegistryLockError, "owner mismatch"):
                lock.release()

    def test_atomic_registry_write_failure_preserves_existing_registry(self) -> None:
        with workspace_tempdir() as temp_dir:
            registry_path = Path(temp_dir) / ".ssot" / "registry.json"
            registry_path.parent.mkdir(parents=True)
            original = {"schema_version": "0.3.0", "repo": {"id": "repo:old"}}
            registry_path.write_text(stable_json_dumps(original), encoding="utf-8")

            with patch("ssot_registry.util.registry_lock.os.replace", side_effect=OSError("replace failed")):
                with self.assertRaises(OSError):
                    save_registry_json_locked(registry_path, {"schema_version": "0.3.0", "repo": {"id": "repo:new"}})

            self.assertEqual(load_json(registry_path), original)
            self.assertFalse(registry_lock_path(registry_path).exists())
            self.assertEqual(list(registry_path.parent.glob(".registry.json.*.tmp")), [])

    def test_production_registry_writes_route_through_save_registry(self) -> None:
        production_root = PROJECT_ROOT / "pkgs" / "ssot-core" / "src" / "ssot_registry" / "api"
        offenders: list[str] = []
        for path in production_root.rglob("*.py"):
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if "save_json(registry_path" in line or ("registry_path.write_text(" in line):
                    offenders.append(f"{path.relative_to(PROJECT_ROOT).as_posix()}:{line_number}")

        self.assertEqual(offenders, [])

    def test_unchecked_registry_writes_are_limited_to_documented_callers(self) -> None:
        production_root = PROJECT_ROOT / "pkgs" / "ssot-core" / "src" / "ssot_registry"
        allowed = {
            "api/__init__.py",
            "api/init.py",
            "api/save.py",
            "control/scaffold.py",
        }
        offenders: list[str] = []
        for path in production_root.rglob("*.py"):
            relative = path.relative_to(production_root).as_posix()
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if "save_registry_unchecked" in line and relative not in allowed:
                    offenders.append(f"{relative}:{line_number}")

        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
