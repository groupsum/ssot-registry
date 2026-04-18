from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import PROJECT_ROOT, temp_repo_from_fixture, workspace_tempdir


COMBINED_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "generate_terminal_screenshots.py"
CLI_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "generate_cli_screenshots.py"
TUI_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "generate_tui_screenshots.py"


class GenerateTerminalScreenshotsTests(unittest.TestCase):
    def _assert_png(self, path: Path) -> None:
        self.assertEqual(path.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

    def test_cli_script_writes_expected_png_assets(self) -> None:
        with workspace_tempdir() as temp_dir:
            cli_root = Path(temp_dir) / "cli-assets"
            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI_SCRIPT_PATH),
                    "--asset-root",
                    str(cli_root),
                ],
                cwd=str(PROJECT_ROOT),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
            self.assertTrue((cli_root / "ssot-cli-help.png").exists())
            self.assertTrue((cli_root / "ssot-cli-boundary-help.png").exists())
            self._assert_png(cli_root / "ssot-cli-help.png")
            self._assert_png(cli_root / "ssot-cli-boundary-help.png")

    def test_tui_script_writes_expected_png_assets(self) -> None:
        repo_fixture = temp_repo_from_fixture("repo_valid")
        self.addCleanup(repo_fixture.cleanup)
        repo = Path(repo_fixture.name) / "repo"
        with workspace_tempdir() as temp_dir:
            tui_root = Path(temp_dir) / "tui-assets"
            result = subprocess.run(
                [
                    sys.executable,
                    str(TUI_SCRIPT_PATH),
                    "--repo",
                    str(repo),
                    "--asset-root",
                    str(tui_root),
                ],
                cwd=str(PROJECT_ROOT),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
            self.assertTrue((tui_root / "ssot-tui-browser.png").exists())
            self.assertTrue((tui_root / "ssot-tui-adrs.png").exists())
            self.assertTrue((tui_root / "ssot-tui-specs.png").exists())
            self.assertTrue((tui_root / "ssot-tui-validated.png").exists())
            self._assert_png(tui_root / "ssot-tui-browser.png")
            self._assert_png(tui_root / "ssot-tui-adrs.png")
            self._assert_png(tui_root / "ssot-tui-specs.png")
            self._assert_png(tui_root / "ssot-tui-validated.png")

    def test_combined_script_still_supports_legacy_flags(self) -> None:
        with workspace_tempdir() as temp_dir:
            cli_root = Path(temp_dir) / "cli-assets"
            result = subprocess.run(
                [
                    sys.executable,
                    str(COMBINED_SCRIPT_PATH),
                    "--cli-only",
                    "--cli-asset-root",
                    str(cli_root),
                ],
                cwd=str(PROJECT_ROOT),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
            self.assertTrue((cli_root / "ssot-cli-help.png").exists())
            self._assert_png(cli_root / "ssot-cli-help.png")


if __name__ == "__main__":
    unittest.main()
