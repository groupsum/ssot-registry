from __future__ import annotations

import json
import shutil
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliOutputFormatsTests(unittest.TestCase):
    def test_list_command_supports_yaml_and_csv(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        yaml_result = run_cli("--output-format", "yaml", "feature", "list", str(repo))
        self.assertEqual(yaml_result.returncode, 0, yaml_result.stderr)
        self.assertIn("passed:", yaml_result.stdout)
        self.assertIn("entities:", yaml_result.stdout)

        csv_result = run_cli("--output-format", "csv", "feature", "list", str(repo))
        self.assertEqual(csv_result.returncode, 0, csv_result.stderr)
        self.assertIn("id,title", csv_result.stdout)

    def test_registry_export_supports_toml(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        result = run_cli("registry", "export", str(repo), "--format", "toml")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        export_path = Path(payload["output_path"])
        self.assertTrue(export_path.exists())
        self.assertIn("[program]", export_path.read_text(encoding="utf-8"))

    def test_registry_export_supports_df(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        result = run_cli("registry", "export", str(repo), "--format", "df")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        export_path = Path(payload["output_path"])
        self.assertTrue(export_path.exists())
        self.assertEqual(export_path.suffix, ".txt")
        table_text = export_path.read_text(encoding="utf-8")
        self.assertIn("schema_version", table_text)
        self.assertIn("| program", table_text)

    def test_graph_export_supports_png_when_dot_is_available(self) -> None:
        if shutil.which("dot") is None:
            self.skipTest("dot is not installed")

        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        result = run_cli("graph", "export", str(repo), "--format", "png")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        export_path = Path(payload["output_path"])
        self.assertTrue(export_path.exists())
        self.assertGreater(export_path.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
