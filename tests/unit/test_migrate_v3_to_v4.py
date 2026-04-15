from __future__ import annotations

import unittest
from pathlib import Path

from ssot_registry.api.load import load_registry
from ssot_registry.api.upgrade import migrate_v3_to_v4
from ssot_registry.version import __version__
from tests.helpers import temp_repo_from_fixture


class MigrateV3ToV4Tests(unittest.TestCase):
    def test_migrate_v3_to_v4_imports_documents_and_renames_specs(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_v3_upgrade")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        _registry_path, repo_root, registry = load_registry(repo)
        migrated = migrate_v3_to_v4(registry, repo_root, previous_version="0.1.2", target_version=__version__)

        self.assertEqual(migrated["schema_version"], 4)
        self.assertEqual(migrated["tooling"]["ssot_registry_version"], __version__)
        self.assertTrue(any(row["id"] == "adr:0001" for row in migrated["adrs"]))
        self.assertTrue(any(row["id"] == "spc:0001" for row in migrated["specs"]))
        self.assertTrue((repo / ".ssot" / "specs" / "SPEC-0001-registry-core.md").exists())
        self.assertFalse((repo / ".ssot" / "specs" / "registry-core.md").exists())


if __name__ == "__main__":
    unittest.main()
