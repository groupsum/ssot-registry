from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_registry import __version__
from tests.helpers import run_cli, temp_repo_from_fixture


class CliUpgradeTests(unittest.TestCase):
    def test_upgrade_migrates_v3_repo_and_is_idempotent(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_v3_upgrade")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        validate_before = run_cli("validate", str(repo))
        self.assertEqual(validate_before.returncode, 1)
        self.assertIn("run `ssot-registry upgrade", validate_before.stdout)

        upgrade = run_cli("upgrade", str(repo), "--target-version", __version__, "--sync-docs", "--write-report")
        self.assertEqual(upgrade.returncode, 0, upgrade.stderr)
        payload = json.loads(upgrade.stdout)
        self.assertIn("migrate_v3_to_v4", payload["migrations"])
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
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        result = run_cli("upgrade", str(repo), "--target-version", __version__)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["passed"])
        self.assertEqual(payload["to_version"], __version__)
        self.assertEqual(payload["migrations"], [])
        self.assertFalse(payload["changed"])


if __name__ == "__main__":
    unittest.main()
