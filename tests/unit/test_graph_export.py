from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_registry.api import export_graph, export_lineage_graph
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
        feature_node = next(node for node in payload["nodes"] if node["id"] == "feat:rfc.9000.connection-migration")
        self.assertEqual(feature_node["title"], "RFC 9000 connection migration")
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

    def test_lineage_graph_export_html(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        result = export_lineage_graph(repo)
        self.assertTrue(result["passed"])
        self.assertEqual(result["format"], "html")
        html = Path(result["output_path"]).read_text(encoding="utf-8")
        self.assertIn("<title>SSOT Lineage Graph</title>", html)
        self.assertIn("Top-down lineage", html)
        self.assertIn("Focus", html)
        self.assertIn("Deselect", html)
        self.assertIn("Barnes-Hut Force", html)
        self.assertIn("Ribbon Culling", html)
        self.assertIn("max:1e4", html)
        self.assertIn("Selected Node", html)
        self.assertIn("Connected Edges", html)
        self.assertIn("Legend", html)
        self.assertIn("toDataURL", html)
        self.assertIn("ssot-lineage-graph.svg", html)
        self.assertIn("pinned", html)
        self.assertIn("window.__SSOT_LINEAGE_PAYLOAD__", html)
        self.assertIn("feat:rfc.9000.connection-migration", html)
        self.assertNotIn("<script src=", html)
        self.assertNotIn('<link rel="stylesheet"', html)
        self.assertNotIn('<link rel="modulepreload"', html)

    def test_dot_export_escapes_newlines_in_ids(self) -> None:
        registry = {
            "features": [{"id": "feat:line\nbreak", "title": "Feature", "description": "", "implementation_status": "absent", "plan": {"horizon": "backlog"}, "lifecycle": {"stage": "active"}, "spec_ids": [], "claim_ids": [], "test_ids": [], "requires": [], "parent_feature_ids": []}],
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
                    "parent_feature_ids": [],
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

    def test_graph_export_includes_feature_parent_contains_edges(self) -> None:
        registry = {
            "features": [
                {"id": "feat:demo.parent", "parent_feature_ids": []},
                {"id": "feat:demo.leaf", "parent_feature_ids": ["feat:demo.parent"]},
            ],
            "specs": [],
            "adrs": [],
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
        self.assertIn({"type": "CONTAINS", "from": "feat:demo.parent", "to": "feat:demo.leaf"}, graph["edges"])

    def test_graph_export_includes_all_release_boundaries(self) -> None:
        registry = {
            "features": [],
            "specs": [],
            "adrs": [],
            "tests": [],
            "claims": [],
            "evidence": [],
            "issues": [],
            "risks": [],
            "boundaries": [{"id": "bnd:a"}, {"id": "bnd:b"}],
            "releases": [{"id": "rel:demo", "boundary_id": "bnd:a", "boundary_ids": ["bnd:a", "bnd:b"]}],
            "profiles": [],
        }
        graph = build_graph_json(registry)
        self.assertIn({"type": "USES_BOUNDARY", "from": "rel:demo", "to": "bnd:a"}, graph["edges"])
        self.assertIn({"type": "USES_BOUNDARY", "from": "rel:demo", "to": "bnd:b"}, graph["edges"])

    def test_graph_export_uses_evidence_centered_proof_edges(self) -> None:
        registry = {
            "features": [{"id": "feat:demo", "title": "Demo"}],
            "specs": [],
            "adrs": [],
            "tests": [{"id": "tst:demo", "title": "Demo test", "evidence_ids": ["evd:demo"], "claim_ids": []}],
            "claims": [{"id": "clm:demo", "title": "Demo claim", "test_ids": [], "evidence_ids": []}],
            "evidence": [{"id": "evd:demo", "title": "Demo evidence", "test_ids": ["tst:demo"], "claim_ids": ["clm:demo"]}],
            "issues": [],
            "risks": [],
            "boundaries": [],
            "releases": [],
            "profiles": [],
        }

        graph = build_graph_json(registry)

        self.assertIn({"type": "PRODUCES", "from": "tst:demo", "to": "evd:demo"}, graph["edges"])
        self.assertIn({"type": "SUPPORTS", "from": "evd:demo", "to": "clm:demo"}, graph["edges"])
        self.assertNotIn({"type": "VERIFIES", "from": "tst:demo", "to": "clm:demo"}, graph["edges"])
        self.assertNotIn({"type": "DERIVES_FROM", "from": "evd:demo", "to": "tst:demo"}, graph["edges"])


if __name__ == "__main__":
    unittest.main()
