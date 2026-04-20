from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_registry.api import export_graph
from ssot_registry.graph.export_dot import build_graph_dot
from tests.helpers import temp_repo_from_fixture


class GraphExportTests(unittest.TestCase):
    def test_graph_export_json(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        result = export_graph(repo, output_format="json")
        self.assertTrue(result["passed"])
        payload = json.loads(Path(result["output_path"]).read_text(encoding="utf-8"))
        node_ids = {node["id"] for node in payload["nodes"]}
        self.assertIn("feat:rfc.9000.connection-migration", node_ids)
        self.assertTrue(any(edge["type"] == "ASSERTS" for edge in payload["edges"]))

    def test_graph_export_dot(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        result = export_graph(repo, output_format="dot")
        self.assertTrue(result["passed"])
        dot_text = Path(result["output_path"]).read_text(encoding="utf-8")
        self.assertIn("digraph ssot_registry", dot_text)
        self.assertIn("feat:rfc.9000.connection-migration", dot_text)

    def test_dot_export_escapes_newlines_in_ids(self) -> None:
        registry = {
            "features": [{"id": "feat:line\nbreak", "title": "Feature", "description": "", "implementation_status": "absent", "plan": {"horizon": "backlog"}, "lifecycle": {"stage": "active"}, "spec_ids": [], "claim_ids": [], "test_ids": [], "requires": []}],
            "tests": [],
            "claims": [],
            "evidence": [],
            "issues": [],
            "risks": [],
            "boundaries": [],
            "releases": [],
        }
        dot_text = build_graph_dot(registry)
        self.assertNotIn('feat:line\nbreak" [label="feat:line\nbreak\n', dot_text)
        self.assertIn('feat:line\\nbreak', dot_text)


if __name__ == "__main__":
    unittest.main()
