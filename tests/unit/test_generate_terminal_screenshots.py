from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import PROJECT_ROOT, workspace_tempdir


COMBINED_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "generate_terminal_screenshots.py"
CLI_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "generate_cli_screenshots.py"
TUI_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "generate_tui_screenshots.py"
EXAMPLE_REPO = PROJECT_ROOT / "examples" / "minimal-repo"


class GenerateTerminalScreenshotsTests(unittest.TestCase):
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

    def test_tui_script_writes_expected_png_assets(self) -> None:
        with workspace_tempdir() as temp_dir:
            tui_root = Path(temp_dir) / "tui-assets"
            result = subprocess.run(
                [
                    sys.executable,
                    str(TUI_SCRIPT_PATH),
                    "--repo",
                    str(EXAMPLE_REPO),
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
            self.assertTrue((tui_root / "ssot-tui-validated.png").exists())

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


if __name__ == "__main__":
    unittest.main()
