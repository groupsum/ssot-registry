from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_registry.api.upgrade import migrate_v0_2_0_to_v0_3_0
from tests.helpers import temp_repo_from_fixture


class MigrateV020ToV030Tests(unittest.TestCase):
    def test_migration_adds_release_boundary_ids_and_bumps_schema(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))
        registry["schema_version"] = "0.2.0"
        for release in registry["releases"]:
            release.pop("boundary_ids", None)

        migrated = migrate_v0_2_0_to_v0_3_0(registry, repo, previous_version="0.2.10", target_version="0.3.0")

        self.assertEqual("0.3.0", migrated["schema_version"])
        for release in migrated["releases"]:
            self.assertEqual([release["boundary_id"]], release["boundary_ids"])

    def test_migration_preserves_existing_extra_boundaries_with_primary_first(self) -> None:
        registry = {
            "schema_version": "0.2.0",
            "releases": [
                {
                    "id": "rel:test",
                    "version": "1.0.0",
                    "status": "draft",
                    "boundary_id": "bnd:primary",
                    "boundary_ids": ["bnd:extra", "bnd:primary"],
                    "claim_ids": [],
                    "evidence_ids": [],
                }
            ],
        }

        migrated = migrate_v0_2_0_to_v0_3_0(registry, Path("."), previous_version="0.2.10", target_version="0.3.0")

        self.assertEqual(["bnd:primary", "bnd:extra"], migrated["releases"][0]["boundary_ids"])


if __name__ == "__main__":
    unittest.main()
