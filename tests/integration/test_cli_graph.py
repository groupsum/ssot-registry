from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliGraphSurfaceTests(unittest.TestCase):
    def test_graph_surface(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        create = run_cli(
            "feature",
            "create",
            str(repo),
            "--id",
            "feat:graph.requires",
            "--title",
            "Graph requires feature",
            "--requires",
            "feat:rfc.9000.connection-migration",
        )
        self.assertEqual(create.returncode, 0, create.stderr)

        export_json = run_cli("graph", "export", str(repo), "--format", "json")
        self.assertEqual(export_json.returncode, 0, export_json.stderr)
        payload = json.loads(Path(json.loads(export_json.stdout)["output_path"]).read_text(encoding="utf-8"))
        self.assertTrue(any(edge["type"] == "REQUIRES" for edge in payload["edges"]))

        export_dot = run_cli("graph", "export", str(repo), "--format", "dot")
        self.assertEqual(export_dot.returncode, 0, export_dot.stderr)
        dot_text = Path(json.loads(export_dot.stdout)["output_path"]).read_text(encoding="utf-8")
        self.assertIn("REQUIRES", dot_text)

        lineage = run_cli("graph", "lineage", str(repo))
        self.assertEqual(lineage.returncode, 0, lineage.stderr)
        lineage_payload = json.loads(lineage.stdout)
        self.assertEqual(lineage_payload["format"], "html")
        self.assertFalse(lineage_payload["opened"])
        html = Path(lineage_payload["output_path"]).read_text(encoding="utf-8")
        self.assertIn("SSOT Lineage Graph", html)
        self.assertIn("Top-down lineage", html)
        self.assertIn("feat:graph.requires", html)

    def test_lineage_rejects_directory_output(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        lineage = run_cli("graph", "lineage", str(repo), "--output", str(repo))

        self.assertNotEqual(lineage.returncode, 0)
        payload = json.loads(lineage.stdout)
        self.assertFalse(payload["passed"])
        self.assertIn("must be a file, not a directory", payload["error"])


if __name__ == "__main__":
    unittest.main()
