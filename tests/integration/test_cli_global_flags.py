from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliGlobalFlagsTests(unittest.TestCase):
    def test_output_file_writes_feature_list_json(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        output_path = repo / ".ssot" / "reports" / "feature-list.json"

        result = run_cli("--output-file", str(output_path), "feature", "list", str(repo))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(output_path.exists())

        stdout_payload = json.loads(result.stdout)
        file_payload = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(file_payload, stdout_payload)
        self.assertIsInstance(file_payload, list)
        self.assertGreater(len(file_payload), 0)

    def test_output_format_and_output_file_work_together(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        output_path = repo / "nested" / "output" / "features.yaml"

        result = run_cli(
            "--output-format",
            "yaml",
            "--output-file",
            str(output_path),
            "feature",
            "list",
            str(repo),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(output_path.exists())

        rendered = output_path.read_text(encoding="utf-8")
        self.assertEqual(rendered, result.stdout)
        self.assertIn("-\n", rendered)
        self.assertIn("id:", rendered)


if __name__ == "__main__":
    unittest.main()
