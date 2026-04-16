from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
for path in (
    REPO_ROOT / "pkgs" / "ssot-registry" / "src",
    REPO_ROOT / "pkgs" / "ssot-codegen" / "src",
    REPO_ROOT / "pkgs" / "ssot-views" / "src",
    REPO_ROOT / "pkgs" / "ssot-contracts" / "src",
    REPO_ROOT / "pkgs" / "ssot-cli" / "src",
    REPO_ROOT / "pkgs" / "ssot-tui" / "src",
    REPO_ROOT / "src",
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
        self.assertIn("adr:0001", list_document_manifest_entries("adr"))
        self.assertTrue(load_schema_text("registry.schema.json").startswith("{"))

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
