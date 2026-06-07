from __future__ import annotations

import argparse
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from ssot_cli.graph_cmd import _open_file, run_lineage
from tests.helpers import workspace_tempdir


class GraphCommandTests(unittest.TestCase):
    def test_run_lineage_opens_generated_file_when_requested(self) -> None:
        temp_dir = workspace_tempdir()
        self.addCleanup(temp_dir.cleanup)
        html = Path(temp_dir.name) / "lineage.html"
        html.write_text("<html></html>", encoding="utf-8")

        with (
            patch(
                "ssot_cli.graph_cmd.export_lineage_graph",
                return_value={"passed": True, "output_path": html.as_posix(), "format": "html"},
            ) as export,
            patch("ssot_cli.graph_cmd._open_file") as opener,
        ):
            payload = run_lineage(argparse.Namespace(path=".", output=None, open=True))

        export.assert_called_once_with(path=".", output=None)
        opener.assert_called_once_with(html)
        self.assertTrue(payload["opened"])

    def test_run_lineage_does_not_open_by_default(self) -> None:
        with (
            patch(
                "ssot_cli.graph_cmd.export_lineage_graph",
                return_value={"passed": True, "output_path": "lineage.html", "format": "html"},
            ),
            patch("ssot_cli.graph_cmd._open_file") as opener,
        ):
            payload = run_lineage(argparse.Namespace(path=".", output=None, open=False))

        opener.assert_not_called()
        self.assertFalse(payload["opened"])

    def test_open_file_uses_windows_startfile(self) -> None:
        if not sys.platform.startswith("win"):
            self.skipTest("Windows opener dispatch is only import-safe on Windows")
        temp_dir = workspace_tempdir()
        self.addCleanup(temp_dir.cleanup)
        html = Path(temp_dir.name) / "lineage.html"
        html.write_text("<html></html>", encoding="utf-8")

        with patch("ssot_cli.graph_cmd.sys.platform", "win32"), patch("ssot_cli.graph_cmd.os.startfile") as startfile:
            _open_file(html)

        startfile.assert_called_once_with(html.resolve())

    def test_open_file_uses_macos_open(self) -> None:
        temp_dir = workspace_tempdir()
        self.addCleanup(temp_dir.cleanup)
        html = Path(temp_dir.name) / "lineage.html"
        html.write_text("<html></html>", encoding="utf-8")

        with patch("ssot_cli.graph_cmd.sys.platform", "darwin"), patch("ssot_cli.graph_cmd.subprocess.Popen") as popen:
            _open_file(html)

        popen.assert_called_once()
        self.assertEqual(popen.call_args.args[0], ["open", str(html.resolve())])

    def test_open_file_uses_linux_xdg_open(self) -> None:
        temp_dir = workspace_tempdir()
        self.addCleanup(temp_dir.cleanup)
        html = Path(temp_dir.name) / "lineage.html"
        html.write_text("<html></html>", encoding="utf-8")

        with patch("ssot_cli.graph_cmd.sys.platform", "linux"), patch("ssot_cli.graph_cmd.subprocess.Popen") as popen:
            _open_file(html)

        popen.assert_called_once()
        self.assertEqual(popen.call_args.args[0], ["xdg-open", str(html.resolve())])

    def test_open_file_rejects_missing_artifact(self) -> None:
        with self.assertRaisesRegex(ValueError, "Cannot open missing lineage graph artifact"):
            _open_file(Path("missing-lineage.html"))


if __name__ == "__main__":
    unittest.main()
