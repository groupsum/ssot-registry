from __future__ import annotations

import unittest
from pathlib import Path

from ssot_contracts.schema import list_schema_names


REPO_ROOT = Path(__file__).resolve().parents[2]


class SchemaInventoryCertificationTests(unittest.TestCase):
    def test_repo_schema_tree_contains_expected_packaged_schema_inventory(self) -> None:
        packaged = set(list_schema_names())
        repo_schemas = {path.name for path in (REPO_ROOT / ".ssot" / "schemas").glob("*.json")}
        self.assertTrue(packaged.issubset(repo_schemas))
        self.assertIn("boundary.snapshot.schema.json", repo_schemas)
        self.assertIn("release.snapshot.schema.json", repo_schemas)
        self.assertIn("published.snapshot.schema.json", repo_schemas)
        self.assertIn("validation.report.schema.json", repo_schemas)
        self.assertIn("certification.report.schema.json", repo_schemas)
        self.assertIn("graph.export.schema.json", repo_schemas)
