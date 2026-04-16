from __future__ import annotations

import unittest
from pathlib import Path

from ssot_registry.api.load import load_registry
from ssot_registry.api.upgrade import migrate_v5_to_v6
from ssot_registry.version import __version__
from tests.helpers import temp_repo_from_fixture


class MigrateV5ToV6Tests(unittest.TestCase):
    def test_migrate_v5_to_v6_normalizes_document_status_fields(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        registry_path = repo / ".ssot" / "registry.json"
        import json

        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["schema_version"] = 5
        registry["adrs"][0]["status"] = "proposed"
        registry["specs"][0].pop("status", None)
        registry["specs"][0].pop("supersedes", None)
        registry["specs"][0].pop("superseded_by", None)
        registry["specs"][0].pop("status_notes", None)

        _registry_path, repo_root, _loaded = load_registry(repo)
        migrated = migrate_v5_to_v6(registry, repo_root, previous_version=__version__, target_version=__version__)
        self.assertEqual(migrated["schema_version"], 6)
        self.assertEqual(migrated["adrs"][0]["status"], "draft")
        self.assertEqual(migrated["specs"][0]["status"], "draft")
        self.assertEqual(migrated["specs"][0]["supersedes"], [])
        self.assertEqual(migrated["specs"][0]["superseded_by"], [])
        self.assertEqual(migrated["specs"][0]["status_notes"], [])


if __name__ == "__main__":
    unittest.main()
