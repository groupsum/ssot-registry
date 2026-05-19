from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
for path in (
    REPO_ROOT / "pkgs" / "ssot-core" / "src",
    REPO_ROOT / "pkgs" / "ssot-codegen" / "src",
    REPO_ROOT / "pkgs" / "ssot-views" / "src",
    REPO_ROOT / "pkgs" / "ssot-contracts" / "src",
    REPO_ROOT / "pkgs" / "ssot-cli" / "src",
    REPO_ROOT / "pkgs" / "ssot-tui" / "src",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ssot_codegen import generate_python_artifacts
from ssot_contracts import list_document_manifest_entries, list_schema_names, load_schema_text
from ssot_views.graph import build_graph_json
from tests.helpers import temp_repo_from_fixture


class ContractsViewsCodegenTests(unittest.TestCase):
    def test_contracts_expose_schema_and_manifest_resources(self) -> None:
        self.assertIn("registry.schema.json", list_schema_names())
        self.assertIn("adr:0600", list_document_manifest_entries("adr"))
        self.assertTrue(load_schema_text("registry.schema.json").startswith("{"))

    def test_registry_schema_exposes_claim_lineage_and_pack_document_provenance(self) -> None:
        schema = json.loads(load_schema_text("registry.schema.json"))
        self.assertEqual(schema["properties"]["schema_version"]["const"], "0.7.0")
        claim_def = schema["$defs"]["claim"]
        self.assertIn("depends_on_claim_ids", claim_def["required"])
        self.assertEqual(claim_def["properties"]["depends_on_claim_ids"], {"$ref": "#/$defs/stringList"})
        feature_def = schema["$defs"]["feature"]
        self.assertIn("parent_feature_ids", feature_def["required"])
        self.assertEqual(feature_def["properties"]["parent_feature_ids"], {"$ref": "#/$defs/stringList"})
        for document_def_name in ("adr", "spec"):
            properties = schema["$defs"][document_def_name]["properties"]
            self.assertIn("source_pack_id", properties)
            self.assertIn("source_package_name", properties)
            self.assertIn("source_document_kind", properties)
            self.assertIn("source_document_id", properties)

    def test_codegen_emits_json_metadata_indexes(self) -> None:
        output_root = REPO_ROOT / ".tmp_test_runs" / "codegen-check"
        written = generate_python_artifacts(output_root)
        self.assertGreaterEqual(len(written), 6)
        payload = json.loads((output_root / "cli.metadata.json").read_text(encoding="utf-8"))
        self.assertIn("output_formats", payload)
        self.assertTrue((output_root / "enums.py").exists())

    def test_views_graph_builder_exports_fixture_registry(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        repo = Path(temp_dir.name) / "repo"
        try:
            registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))
        finally:
            temp_dir.cleanup()
        graph = build_graph_json(registry)
        self.assertIn("nodes", graph)
        self.assertIn("edges", graph)


if __name__ == "__main__":
    unittest.main()
