from __future__ import annotations

import unittest
from pathlib import Path

from ssot_registry.api import upgrade
from ssot_registry.model.enums import SCHEMA_VERSION
from ssot_registry.model.schema_version import LEGACY_SCHEMA_VERSIONS, SUPPORTED_SEMVER_SCHEMA_VERSIONS


class MigrationPathTests(unittest.TestCase):
    def test_all_non_current_known_schema_versions_have_a_migration_path(self) -> None:
        source_versions = {source for source, _target, _function_name in upgrade.MIGRATION_PATHS}
        known_non_current = set(LEGACY_SCHEMA_VERSIONS) | (set(SUPPORTED_SEMVER_SCHEMA_VERSIONS) - {SCHEMA_VERSION})

        self.assertEqual(known_non_current, source_versions)

    def test_migration_paths_have_callable_implementations_and_release_labels(self) -> None:
        for source, target, function_name in upgrade.MIGRATION_PATHS:
            with self.subTest(source=source, target=target):
                self.assertTrue(callable(getattr(upgrade, function_name, None)))
                self.assertIn((source, target), upgrade.MIGRATION_RELEASE_WINDOWS)

    def test_migration_paths_form_a_route_to_current_schema(self) -> None:
        path_by_source = {source: target for source, target, _function_name in upgrade.MIGRATION_PATHS}

        for source in path_by_source:
            with self.subTest(source=source):
                seen: set[object] = set()
                current = source
                while current != SCHEMA_VERSION:
                    self.assertNotIn(current, seen)
                    seen.add(current)
                    self.assertIn(current, path_by_source)
                    current = path_by_source[current]

    def test_v0_5_to_v0_6_adds_claim_lineage_defaults_without_splitting_claims(self) -> None:
        registry = {
            "schema_version": "0.5.0",
            "claims": [
                {
                    "id": "clm:example.t1",
                    "title": "Example T1 claim",
                    "status": "asserted",
                    "tier": "T1",
                    "kind": "conformance",
                    "description": "example",
                    "feature_ids": ["feat:example"],
                    "test_ids": [],
                    "evidence_ids": [],
                    "origin": "repo-local",
                }
            ],
        }

        migrated = upgrade.migrate_v0_5_0_to_v0_6_0(
            registry,
            Path("."),
            previous_version="0.2.10",
            target_version="0.2.10",
        )

        self.assertEqual(migrated["schema_version"], upgrade.SCHEMA_V0_6_0)
        self.assertEqual(len(migrated["claims"]), 1)
        self.assertEqual(migrated["claims"][0]["id"], "clm:example.t1")
        self.assertEqual(migrated["claims"][0]["tier"], "T1")
        self.assertEqual(migrated["claims"][0]["depends_on_claim_ids"], [])

    def test_v0_6_to_v0_7_adds_feature_parent_defaults_without_rewriting_requires(self) -> None:
        registry = {
            "schema_version": "0.6.0",
            "features": [
                {
                    "id": "feat:example.leaf",
                    "title": "Leaf",
                    "requires": ["feat:example.prereq"],
                },
                {
                    "id": "feat:example.child",
                    "title": "Child",
                    "requires": [],
                    "parent_feature_ids": ["feat:example.parent", "feat:example.parent", "feat:example.other"],
                },
            ],
        }

        migrated = upgrade.migrate_v0_6_0_to_v0_7_0(
            registry,
            Path("."),
            previous_version="0.2.10",
            target_version="0.2.10",
        )

        self.assertEqual(migrated["schema_version"], SCHEMA_VERSION)
        self.assertEqual(migrated["features"][0]["requires"], ["feat:example.prereq"])
        self.assertEqual(migrated["features"][0]["parent_feature_ids"], [])
        self.assertEqual(
            migrated["features"][1]["parent_feature_ids"],
            ["feat:example.other", "feat:example.parent"],
        )


if __name__ == "__main__":
    unittest.main()
