from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_registry.api.upgrade import migrate_v10_to_v0_1_0
from tests.helpers import temp_repo_from_fixture


class MigrateV10ToV010Tests(unittest.TestCase):
    def test_migration_relabels_schema_version_to_semver(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["schema_version"] = 10

        migrated = migrate_v10_to_v0_1_0(registry, repo, previous_version="0.2.7", target_version="0.2.7")

        self.assertEqual("0.2.0", migrated["schema_version"])
        self.assertTrue(migrated["features"])
        for feature in migrated["features"]:
            self.assertIn("spec_ids", feature)
        for spec in migrated["specs"]:
            self.assertIn("adr_ids", spec)


if __name__ == "__main__":
    unittest.main()
