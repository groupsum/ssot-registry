from __future__ import annotations

import json
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

    def test_release_snapshot_schema_declares_plural_boundary_fields(self) -> None:
        schema_path = REPO_ROOT / ".ssot" / "schemas" / "release.snapshot.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))

        self.assertIn("boundaries", schema["required"])
        self.assertIn("profiles", schema["required"])
        self.assertIn("profile_evaluations", schema["required"])
        self.assertEqual(schema["properties"]["release"]["properties"]["boundary_ids"]["type"], "array")
        self.assertEqual(schema["properties"]["summary"]["properties"]["boundary_ids"]["type"], "array")
        self.assertEqual(schema["properties"]["summary"]["properties"]["boundary_count"]["type"], "integer")
