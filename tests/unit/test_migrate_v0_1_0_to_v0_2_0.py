from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_registry.api.upgrade import migrate_v0_1_0_to_v0_2_0
from tests.helpers import temp_repo_from_fixture


class MigrateV010ToV020Tests(unittest.TestCase):
    def test_migration_adds_empty_spec_adr_ids_and_bumps_schema(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))
        registry["schema_version"] = "0.1.0"

        migrated = migrate_v0_1_0_to_v0_2_0(registry, repo, previous_version="0.2.10", target_version="0.2.10")

        self.assertEqual("0.2.0", migrated["schema_version"])
        self.assertTrue(migrated["specs"])
        for spec in migrated["specs"]:
            self.assertIn("adr_ids", spec)
            self.assertEqual(spec["adr_ids"], [])


if __name__ == "__main__":
    unittest.main()
