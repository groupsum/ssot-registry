from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliUpgradeTests(unittest.TestCase):
    def test_upgrade_migrates_v3_repo_and_is_idempotent(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_v3_upgrade")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        validate_before = run_cli("validate", str(repo))
        self.assertEqual(validate_before.returncode, 1)
        self.assertIn("run `ssot-registry upgrade", validate_before.stdout)

        upgrade = run_cli("upgrade", str(repo), "--sync-docs", "--write-report")
        self.assertEqual(upgrade.returncode, 0, upgrade.stderr)
        payload = json.loads(upgrade.stdout)
        self.assertIn("migrate_v3_to_v4", payload["migrations"])
        self.assertTrue((repo / ".ssot" / "specs" / "SPEC-0001-registry-core.md").exists())
        self.assertFalse((repo / ".ssot" / "specs" / "registry-core.md").exists())
        self.assertTrue((repo / ".ssot" / "reports" / "upgrade.report.json").exists())

        validate_after = run_cli("validate", str(repo))
        self.assertEqual(validate_after.returncode, 0, validate_after.stderr)

        second_upgrade = run_cli("upgrade", str(repo), "--sync-docs")
        self.assertEqual(second_upgrade.returncode, 0, second_upgrade.stderr)
        second_payload = json.loads(second_upgrade.stdout)
        self.assertEqual(second_payload["sync"]["adr"]["created"], [])
        self.assertEqual(second_payload["sync"]["spec"]["created"], [])


if __name__ == "__main__":
    unittest.main()
