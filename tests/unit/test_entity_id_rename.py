from __future__ import annotations

import unittest
from pathlib import Path

from ssot_registry.api import update_entity, validate_registry
from ssot_registry.api.load import load_registry
from tests.helpers import temp_repo_from_fixture


class EntityIdRenameTests(unittest.TestCase):
    def test_feature_id_rename_rewrites_all_references(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        old_id = "feat:rfc.9000.connection-migration"
        new_id = "feat:rfc.9000.connection-migration.renamed"
        result = update_entity(repo, "features", old_id, {"id": new_id})
        self.assertTrue(result["passed"])
        self.assertEqual(result["entity"]["id"], new_id)

        _registry_path, _repo_root, registry = load_registry(repo)

        for section in ("profiles", "tests", "claims", "issues", "risks", "boundaries"):
            for row in registry.get(section, []):
                feature_ids = row.get("feature_ids")
                if isinstance(feature_ids, list):
                    self.assertNotIn(old_id, feature_ids)

        for row in registry.get("features", []):
            requires = row.get("requires")
            if isinstance(requires, list):
                self.assertNotIn(old_id, requires)

        report = validate_registry(repo)
        self.assertTrue(report["passed"], report)

    def test_boundary_id_rename_updates_program_and_release_references(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        _registry_path, _repo_root, registry_before = load_registry(repo)
        old_id = registry_before.get("program", {}).get("active_boundary_id")
        self.assertIsInstance(old_id, str)
        new_id = f"{old_id}.renamed"
        result = update_entity(repo, "boundaries", old_id, {"id": new_id})
        self.assertTrue(result["passed"])
        self.assertEqual(result["entity"]["id"], new_id)

        _registry_path, _repo_root, registry = load_registry(repo)
        self.assertEqual(registry.get("program", {}).get("active_boundary_id"), new_id)
        release_boundary_ids = {row.get("boundary_id") for row in registry.get("releases", [])}
        self.assertIn(new_id, release_boundary_ids)
        self.assertNotIn(old_id, release_boundary_ids)

        report = validate_registry(repo)
        self.assertTrue(report["passed"], report)


if __name__ == "__main__":
    unittest.main()
