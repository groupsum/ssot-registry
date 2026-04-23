from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[2]
for path in (
    REPO_ROOT / "pkgs" / "ssot-core" / "src",
    REPO_ROOT / "pkgs" / "ssot-codegen" / "src",
    REPO_ROOT / "pkgs" / "ssot-views" / "src",
    REPO_ROOT / "pkgs" / "ssot-contracts" / "src",
    REPO_ROOT / "pkgs" / "ssot-tui" / "src",
    REPO_ROOT / "pkgs" / "ssot-cli" / "src",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ssot_cli.main import build_parser
from ssot_registry.cli.main import main as compatibility_main
from ssot_tui.services import RegistryWorkspaceService
from tests.helpers import temp_repo_from_fixture


class CliPackageLayoutTests(unittest.TestCase):
    def test_ssot_cli_parser_builds_expected_global_flags(self) -> None:
        parser = build_parser(prog="ssot")
        options = {flag for action in parser._actions for flag in action.option_strings}
        self.assertIn("--output-format", options)
        self.assertIn("--output-file", options)

    def test_entity_parsers_expose_semantic_descriptions(self) -> None:
        parser = build_parser(prog="ssot")
        subparsers_action = next(action for action in parser._actions if action.dest == "command")

        self.assertIn("decision history", subparsers_action.choices["adr"].description)
        self.assertIn("normative or operational contract", subparsers_action.choices["spec"].description)
        self.assertIn("targetable implementation units", subparsers_action.choices["feature"].description)
        self.assertIn("scoped set of direct features and reusable profiles", subparsers_action.choices["boundary"].description)

    def test_compatibility_entrypoint_reexports_main(self) -> None:
        self.assertIsNotNone(compatibility_main)

    def test_registry_workspace_service_loads_repo_valid_fixture(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        repo = Path(temp_dir.name) / "repo"
        try:
            workspace = RegistryWorkspaceService().load_workspace(repo)
        finally:
            temp_dir.cleanup()

        self.assertIn("passed", workspace.validation)
        self.assertIn("features", workspace.collections)
        self.assertIsInstance(workspace.repo, dict)

    @unittest.skipUnless(importlib.util.find_spec("textual") is not None, "textual is not installed")
    def test_textual_app_imports(self) -> None:
        from ssot_tui.app import SsotTuiApp

        app = SsotTuiApp()
        self.assertEqual(app.TITLE, "SSOT TUI")

    @unittest.skipUnless(importlib.util.find_spec("textual") is not None, "textual is not installed")
    def test_textual_app_ctrl_c_hard_exits_with_interrupt_code(self) -> None:
        from ssot_tui.app import SsotTuiApp

        app = SsotTuiApp()
        with patch.object(app, "exit") as exit_mock:
            app.action_hard_exit()

        exit_mock.assert_called_once_with(return_code=130)

    def test_tui_main_converts_keyboard_interrupt_to_exit_code_130(self) -> None:
        from ssot_tui.main import main

        with patch("ssot_tui.main.SsotTuiApp") as app_cls:
            app_cls.return_value.run.side_effect = KeyboardInterrupt
            self.assertEqual(main(), 130)


if __name__ == "__main__":
    unittest.main()
