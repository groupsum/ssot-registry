from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_registry.api import export_graph
from ssot_registry.graph.export_dot import build_graph_dot
from ssot_views.graph import build_graph_json
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
            "adrs": [],
            "specs": [],
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

    def test_graph_export_includes_spec_to_adr_and_derived_feature_edges(self) -> None:
        registry = {
            "features": [
                {
                    "id": "feat:demo.spec-adr",
                    "title": "Feature",
                    "description": "",
                    "implementation_status": "implemented",
                    "plan": {"horizon": "current", "target_claim_tier": "T1", "slot": None, "target_lifecycle_stage": "active"},
                    "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
                    "spec_ids": ["spc:demo.spec-adr"],
                    "claim_ids": [],
                    "test_ids": [],
                    "requires": [],
                }
            ],
            "specs": [{"id": "spc:demo.spec-adr", "adr_ids": ["adr:demo.decision"]}],
            "adrs": [{"id": "adr:demo.decision"}],
            "tests": [],
            "claims": [],
            "evidence": [],
            "issues": [],
            "risks": [],
            "boundaries": [],
            "releases": [],
            "profiles": [],
        }
        graph = build_graph_json(registry)
        self.assertIn({"type": "SPECIFIED_BY", "from": "feat:demo.spec-adr", "to": "spc:demo.spec-adr"}, graph["edges"])
        self.assertIn({"type": "DECIDED_BY", "from": "spc:demo.spec-adr", "to": "adr:demo.decision"}, graph["edges"])
        self.assertIn({"type": "DECIDED_BY", "from": "feat:demo.spec-adr", "to": "adr:demo.decision"}, graph["edges"])


if __name__ == "__main__":
    unittest.main()
