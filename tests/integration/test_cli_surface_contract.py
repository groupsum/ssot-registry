from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.generate_cli_surface_manifest import generate_manifest
from tests.helpers import PROJECT_ROOT, run_cli, temp_repo_from_fixture


MANIFEST_PATH = PROJECT_ROOT / "tests" / "fixtures" / "cli_surface_manifest.json"
README_PATH = PROJECT_ROOT / "pkgs" / "ssot-cli" / "README.md"


class CliSurfaceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_checked_in_manifest_matches_live_parser(self) -> None:
        self.assertEqual(self.manifest, generate_manifest())

    def test_readme_lists_every_live_command_path_and_flag(self) -> None:
        readme = README_PATH.read_text(encoding="utf-8")
        for command in self.manifest["top_level_commands"]:
            self.assertIn(f"`ssot-registry {command}`", readme, command)

        for path in self.manifest["subcommand_paths"]:
            self.assertIn(f"`ssot-registry {path}`", readme, path)
            for flag in self.manifest["flags_by_path"][path]:
                self.assertIn(f"`{flag}`", readme, f"{path} {flag}")

        for flag in self.manifest["global_flags"]:
            self.assertIn(f"`{flag}`", readme, flag)

    def test_every_command_path_has_valid_help_output(self) -> None:
        for path in self.manifest["subcommand_paths"]:
            with self.subTest(path=path):
                result = run_cli(*path.split(), "--help")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("usage:", result.stdout)
                self.assertIn(path.split()[0], result.stdout)
                for flag in self.manifest["flags_by_path"][path]:
                    self.assertIn(flag, result.stdout)

    def test_every_command_path_reports_invalid_flag_output(self) -> None:
        invalid_flag = "--unknown-ssot-contract-flag"
        for path in self.manifest["subcommand_paths"]:
            with self.subTest(path=path):
                result = run_cli(*path.split(), invalid_flag)
                self.assertNotEqual(result.returncode, 0)
                combined = result.stdout + result.stderr
                self.assertIn("usage:", combined)
                self.assertTrue(
                    invalid_flag in combined
                    or "the following arguments are required" in combined
                    or "one of the arguments" in combined
                    or "invalid choice" in combined,
                    combined,
                )

    def test_global_flags_have_valid_and_invalid_output_contracts(self) -> None:
        version = run_cli("--version")
        self.assertEqual(version.returncode, 0, version.stderr)
        self.assertIn("ssot-registry", version.stdout)

        help_result = run_cli("--help")
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        for flag in self.manifest["global_flags"]:
            self.assertIn(flag, help_result.stdout)

        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        for output_format in ("json", "yaml", "toml", "csv", "df"):
            with self.subTest(output_format=output_format):
                result = run_cli("--output-format", output_format, "feature", "list", str(repo))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(result.stdout.strip())

        invalid_format = run_cli("--output-format", "xml", "feature", "list", str(repo))
        self.assertNotEqual(invalid_format.returncode, 0)
        self.assertIn("invalid choice", invalid_format.stderr)
        self.assertIn("--output-format", invalid_format.stderr)


if __name__ == "__main__":
    unittest.main()
