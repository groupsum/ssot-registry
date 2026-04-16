from __future__ import annotations

import unittest
from pathlib import Path

from ssot_registry.api.load import load_registry
from ssot_registry.api.upgrade import migrate_v4_to_v5
from ssot_registry.version import __version__
from tests.helpers import temp_repo_from_fixture


class MigrateV4ToV5Tests(unittest.TestCase):
    def test_migrate_v4_to_v5_adds_profiles_section_and_boundary_profile_ids(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        registry_path = repo / ".ssot" / "registry.json"
        import json

        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["schema_version"] = 4
        registry.pop("profiles", None)
        for boundary in registry.get("boundaries", []):
            boundary.pop("profile_ids", None)

        _registry_path, repo_root, _loaded = load_registry(repo)
        migrated = migrate_v4_to_v5(registry, repo_root, previous_version=__version__, target_version=__version__)
        self.assertEqual(migrated["schema_version"], 5)
        self.assertIn("profiles", migrated)
        self.assertIsInstance(migrated["profiles"], list)
        self.assertIn("profile_ids", migrated["boundaries"][0])


if __name__ == "__main__":
    unittest.main()
