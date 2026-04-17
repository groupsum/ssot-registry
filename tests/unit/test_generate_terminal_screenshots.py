from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import PROJECT_ROOT, workspace_tempdir


SCRIPT_PATH = PROJECT_ROOT / "scripts" / "generate_terminal_screenshots.py"
EXAMPLE_REPO = PROJECT_ROOT / "examples" / "minimal-repo"


class GenerateTerminalScreenshotsTests(unittest.TestCase):
    def test_cli_only_writes_expected_svg_assets(self) -> None:
        with workspace_tempdir() as temp_dir:
            cli_root = Path(temp_dir) / "cli-assets"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
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
            self.assertTrue((cli_root / "ssot-cli-help.svg").exists())
            self.assertTrue((cli_root / "ssot-cli-boundary-help.svg").exists())

    def test_tui_only_writes_expected_svg_assets(self) -> None:
        with workspace_tempdir() as temp_dir:
            tui_root = Path(temp_dir) / "tui-assets"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--tui-only",
                    "--repo",
                    str(EXAMPLE_REPO),
                    "--tui-asset-root",
                    str(tui_root),
                ],
                cwd=str(PROJECT_ROOT),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
            self.assertTrue((tui_root / "ssot-tui-browser.svg").exists())
            self.assertTrue((tui_root / "ssot-tui-validated.svg").exists())


if __name__ == "__main__":
    unittest.main()
