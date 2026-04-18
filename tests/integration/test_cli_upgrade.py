from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORE_SRC_ROOT = PROJECT_ROOT / "pkgs" / "ssot-core" / "src"
if str(CORE_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(CORE_SRC_ROOT))

from ssot_registry import __version__
from tests.helpers import run_cli, temp_repo_from_fixture, workspace_tempdir


class CliUpgradeTests(unittest.TestCase):
    def test_upgrade_migrates_v3_repo_and_is_idempotent(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_v3_upgrade")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        validate_before = run_cli("validate", str(repo))
        self.assertEqual(validate_before.returncode, 1)
        self.assertIn("run `ssot upgrade", validate_before.stdout)

        upgrade = run_cli("upgrade", str(repo), "--target-version", __version__, "--sync-docs", "--write-report")
        self.assertEqual(upgrade.returncode, 0, upgrade.stderr)
        payload = json.loads(upgrade.stdout)
        self.assertIn("0.1.x->0.2.1 (schema 3->4)", payload["migrations"])
        self.assertIn("migrate_v3_to_v4", payload["schema_migrations"])
        self.assertEqual(payload["to_version"], __version__)
        self.assertTrue((repo / ".ssot" / "specs" / "SPEC-0600-registry-core.yaml").exists())
        self.assertFalse((repo / ".ssot" / "specs" / "registry-core.md").exists())
        self.assertTrue((repo / ".ssot" / "reports" / "upgrade.report.json").exists())

        validate_after = run_cli("validate", str(repo))
        self.assertEqual(validate_after.returncode, 0, validate_after.stderr)

        second_upgrade = run_cli("upgrade", str(repo), "--target-version", __version__, "--sync-docs")
        self.assertEqual(second_upgrade.returncode, 0, second_upgrade.stderr)
        second_payload = json.loads(second_upgrade.stdout)
        self.assertEqual(second_payload["sync"]["adr"]["created"], [])
        self.assertEqual(second_payload["sync"]["spec"]["created"], [])

    def test_upgrade_target_version_allows_noop_for_current_version(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            init = run_cli("init", str(repo), "--repo-id", "repo:upgrade-noop", "--repo-name", "upgrade-noop", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            result = run_cli("upgrade", str(repo), "--target-version", __version__)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["passed"])
            self.assertEqual(payload["to_version"], __version__)
            self.assertEqual(payload["migrations"], [])
            self.assertEqual(payload["schema_migrations"], [])
            self.assertFalse(payload["changed"])


if __name__ == "__main__":
    unittest.main()
