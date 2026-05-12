from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_registry.api.upgrade import migrate_v0_3_0_to_v0_4_0
from tests.helpers import temp_repo_from_fixture


class MigrateV030ToV040Tests(unittest.TestCase):
    def test_migration_only_bumps_schema_version(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))
        registry["schema_version"] = "0.3.0"
        snapshot = json.loads(json.dumps(registry))

        migrated = migrate_v0_3_0_to_v0_4_0(registry, repo, previous_version="0.2.10", target_version="0.4.0")

        self.assertEqual("0.4.0", migrated["schema_version"])
        snapshot["schema_version"] = "0.4.0"
        self.assertEqual(snapshot, migrated)


if __name__ == "__main__":
    unittest.main()
