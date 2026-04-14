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


if __name__ == "__main__":
    unittest.main()
