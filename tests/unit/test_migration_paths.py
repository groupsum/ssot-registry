from __future__ import annotations

import unittest

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


if __name__ == "__main__":
    unittest.main()
