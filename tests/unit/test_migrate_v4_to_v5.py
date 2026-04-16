from __future__ import annotations

import unittest
from pathlib import Path

from ssot_registry.api.load import load_registry
from ssot_registry.api.upgrade import migrate_v4_to_v5
from tests.helpers import temp_repo_from_fixture


class MigrateV4ToV5Tests(unittest.TestCase):
    def test_migrate_v4_to_v5_adds_profiles_section_and_boundary_profile_ids(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        _registry_path, repo_root, registry = load_registry(repo)
        registry["schema_version"] = 4
        registry.pop("profiles", None)
        for boundary in registry.get("boundaries", []):
            boundary.pop("profile_ids", None)

        migrated = migrate_v4_to_v5(registry, repo_root, previous_version="0.2.0", target_version="0.3.0")

        self.assertEqual(migrated["schema_version"], 5)
        self.assertIn("profiles", migrated)
        self.assertIsInstance(migrated["profiles"], list)
        self.assertIn("profile_ids", migrated["boundaries"][0])
        self.assertEqual(migrated["boundaries"][0]["profile_ids"], [])


if __name__ == "__main__":
    unittest.main()
