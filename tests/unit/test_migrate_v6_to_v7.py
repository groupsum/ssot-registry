from __future__ import annotations

import unittest
from pathlib import Path

from ssot_registry.api.upgrade import migrate_v6_to_v7
from tests.helpers import temp_repo_from_fixture


class MigrateV6ToV7Tests(unittest.TestCase):
    def test_migration_sets_repo_kind_and_reclassifies_docs(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        registry_path = repo / ".ssot" / "registry.json"
        import json

        original = json.loads(registry_path.read_text(encoding="utf-8"))
        migrated = migrate_v6_to_v7(original, repo, previous_version="0.2.1", target_version="0.2.1")

        self.assertEqual(7, migrated["schema_version"])
        self.assertEqual("repo-local", migrated["repo"]["kind"])
        self.assertEqual("ssot-origin", migrated["adrs"][0]["origin"])
        self.assertEqual("ssot-origin", migrated["specs"][0]["origin"])
        self.assertEqual("ssot-core", migrated["document_id_reservations"]["adr"][0]["owner"])
        self.assertEqual(1, migrated["document_id_reservations"]["adr"][0]["start"])
        self.assertEqual("ssot-origin", migrated["document_id_reservations"]["adr"][1]["owner"])
        self.assertEqual(600, migrated["document_id_reservations"]["adr"][1]["start"])


if __name__ == "__main__":
    unittest.main()
