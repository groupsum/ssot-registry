from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.generate_cli_surface_manifest import generate_manifest
from ssot_mcp.tools import configure_repo, get_ssot_cli_surface, run_ssot_cli
from tests.helpers import PROJECT_ROOT, temp_repo_from_fixture


MANIFEST_PATH = PROJECT_ROOT / "tests" / "fixtures" / "cli_surface_manifest.json"


class McpCliSurfaceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.live_manifest = generate_manifest()

    def tearDown(self) -> None:
        configure_repo(None)

    def test_mcp_cli_surface_matches_live_parser_manifest(self) -> None:
        surface = get_ssot_cli_surface()

        self.assertTrue(surface["passed"])
        self.assertEqual(surface["global_flags"], self.live_manifest["global_flags"])
        self.assertEqual(surface["top_level_commands"], self.live_manifest["top_level_commands"])
        self.assertEqual(surface["subcommand_paths"], self.live_manifest["subcommand_paths"])
        self.assertEqual(surface["flags_by_path"], self.live_manifest["flags_by_path"])

    def test_mcp_every_command_path_has_valid_help_output(self) -> None:
        for path in self.manifest["subcommand_paths"]:
            with self.subTest(path=path):
                result = run_ssot_cli(args=[*path.split(), "--help"])
                self.assertEqual(result["exit_code"], 0, result["stderr"])
                self.assertTrue(result["passed"])
                self.assertIn("usage:", result["stdout"])
                self.assertIn(path.split()[0], result["stdout"])
                for flag in self.manifest["flags_by_path"][path]:
                    self.assertIn(flag, result["stdout"])

    def test_mcp_every_command_path_reports_invalid_flag_output(self) -> None:
        invalid_flag = "--unknown-ssot-contract-flag"
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        for path in self.manifest["subcommand_paths"]:
            with self.subTest(path=path):
                result = run_ssot_cli(repo=str(repo), args=[*path.split(), invalid_flag])
                self.assertNotEqual(result["exit_code"], 0)
                self.assertFalse(result["passed"])
                combined = result["stdout"] + result["stderr"]
                self.assertIn("usage:", combined)
                self.assertTrue(
                    invalid_flag in combined
                    or "the following arguments are required" in combined
                    or "one of the arguments" in combined
                    or "invalid choice" in combined,
                    combined,
                )

    def test_mcp_global_flags_have_valid_and_invalid_output_contracts(self) -> None:
        version = run_ssot_cli(args=["--version"])
        self.assertEqual(version["exit_code"], 0, version["stderr"])
        self.assertIn("ssot-registry", version["stdout"])

        help_result = run_ssot_cli(args=["--help"])
        self.assertEqual(help_result["exit_code"], 0, help_result["stderr"])
        for flag in self.manifest["global_flags"]:
            self.assertIn(flag, help_result["stdout"])

        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        for output_format in ("json", "yaml", "toml", "csv", "df"):
            with self.subTest(output_format=output_format):
                result = run_ssot_cli(
                    repo=str(repo),
                    args=["--output-format", output_format, "feature", "list", "."],
                )
                self.assertEqual(result["exit_code"], 0, result["stderr"])
                self.assertTrue(result["stdout"].strip())

        output_file = repo / "mcp-surface-output.json"
        output_file_result = run_ssot_cli(
            repo=str(repo),
            args=["--output-file", str(output_file), "feature", "list", "."],
        )
        self.assertEqual(output_file_result["exit_code"], 0, output_file_result["stderr"])
        self.assertTrue(output_file.exists())
        self.assertTrue(output_file.read_text(encoding="utf-8").strip())

        invalid_format = run_ssot_cli(
            repo=str(repo),
            args=["--output-format", "xml", "feature", "list", "."],
        )
        self.assertNotEqual(invalid_format["exit_code"], 0)
        self.assertIn("invalid choice", invalid_format["stderr"])
        self.assertIn("--output-format", invalid_format["stderr"])


if __name__ == "__main__":
    unittest.main()
