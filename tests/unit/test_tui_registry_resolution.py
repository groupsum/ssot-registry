from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest
import uuid

from ssot_registry.util.fs import resolve_registry_path
from ssot_tui.persistence import SessionStore
from ssot_tui.services import RegistryWorkspaceService
from tests.helpers import temp_repo_from_fixture

if importlib.util.find_spec("textual") is not None:
    from textual.app import App, ComposeResult

    from ssot_tui.screens.browser import BrowserScreen
    from ssot_tui.widgets import EntityDetailPane, EntityTable
else:
    BrowserScreen = None


class TuiRegistryResolutionTests(unittest.TestCase):
    def test_resolve_registry_path_accepts_ssot_directory(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        repo = Path(temp_dir.name) / "repo"
        try:
            registry_path = resolve_registry_path(repo / ".ssot")
        finally:
            temp_dir.cleanup()

        self.assertEqual(registry_path, repo / ".ssot" / "registry.json")

    def test_resolve_registry_path_walks_up_from_nested_directory(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        repo = Path(temp_dir.name) / "repo"
        nested = repo / "nested" / "deep"
        nested.mkdir(parents=True)
        try:
            registry_path = resolve_registry_path(nested)
        finally:
            temp_dir.cleanup()

        self.assertEqual(registry_path, repo / ".ssot" / "registry.json")

    def test_workspace_service_loads_from_nested_directory(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        repo = Path(temp_dir.name) / "repo"
        try:
            workspace = RegistryWorkspaceService().load_workspace(repo / "tests")
        finally:
            temp_dir.cleanup()

        self.assertEqual(Path(workspace.registry_path), repo / ".ssot" / "registry.json")
        self.assertEqual(Path(workspace.root_path), repo)
        self.assertIn("features", workspace.collections)

    def test_resolve_registry_path_missing_repo_reports_operator_friendly_error(self) -> None:
        missing = Path(Path.cwd().anchor) / f"ssot-missing-{uuid.uuid4()}" / "outside" / "repo"
        with self.assertRaises(FileNotFoundError) as ctx:
            resolve_registry_path(missing)

        message = str(ctx.exception)
        self.assertIn("Unable to locate .ssot/registry.json", message)
        self.assertIn("Provide the repository root", message)

    @unittest.skipUnless(BrowserScreen is not None, "textual is not installed")
    def test_browser_formats_missing_registry_error_for_operator(self) -> None:
        message = BrowserScreen()._format_load_error(
            "C:/work/repo/subdir",
            FileNotFoundError("no registry"),
        )
        self.assertIn("Registry not found", message)
        self.assertIn(".ssot directory", message)

    @unittest.skipUnless(BrowserScreen is not None, "textual is not installed")
    def test_browser_formats_invalid_json_error_with_line_and_column(self) -> None:
        try:
            json.loads("{")
        except json.JSONDecodeError as exc:
            message = BrowserScreen()._format_load_error("C:/work/repo/.ssot/registry.json", exc)
        else:
            self.fail("Expected JSONDecodeError")

        self.assertIn("Registry JSON is invalid", message)
        self.assertIn("line 1, column 2", message)


@unittest.skipUnless(BrowserScreen is not None, "textual is not installed")
class TuiBrowserInteractionTests(unittest.IsolatedAsyncioTestCase):
    async def test_browser_auto_loads_and_populates_table(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        repo = Path(temp_dir.name) / "repo"
        session_root = Path(temp_dir.name) / "session"

        class TestApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(BrowserScreen(initial_path=repo, session_store=SessionStore(session_root)))

        try:
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                screen = app.screen
                table = screen.query_one(EntityTable)
                self.assertIsNotNone(screen.workspace)
                self.assertGreater(table.row_count, 0)
                self.assertEqual(screen.query_one("#repo_path").value, repo.as_posix())
        finally:
            temp_dir.cleanup()

    async def test_resource_traversal_jumps_to_linked_entity(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        repo = Path(temp_dir.name) / "repo"
        session_root = Path(temp_dir.name) / "session"

        class TestApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(BrowserScreen(initial_path=repo, session_store=SessionStore(session_root)))

        try:
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                screen = app.screen
                screen._select_entity_id("feat:rfc.9000.connection-migration")
                await pilot.pause()

                detail = screen.query_one(EntityDetailPane)
                target = next(target for target in detail._targets.values() if target.value == "clm:rfc.9000.connection-migration.t3")
                screen.on_entity_detail_pane_resource_selected(EntityDetailPane.ResourceSelected(detail, target))
                await pilot.pause()

                self.assertEqual(screen.active_section, "claims")
                selected = screen.query_one(EntityTable).entity_for_row_index(screen.query_one(EntityTable).cursor_row)
                self.assertIsNotNone(selected)
                self.assertEqual(selected["id"], "clm:rfc.9000.connection-migration.t3")
        finally:
            temp_dir.cleanup()

    async def test_resource_traversal_previews_file_resource(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        repo = Path(temp_dir.name) / "repo"
        session_root = Path(temp_dir.name) / "session"

        class TestApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(BrowserScreen(initial_path=repo, session_store=SessionStore(session_root)))

        try:
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                screen = app.screen
                screen._select_entity_id("tst:pytest.rfc.9000.connection-migration")
                await pilot.pause()

                detail = screen.query_one(EntityDetailPane)
                target = next(target for target in detail._targets.values() if target.kind == "file")
                screen.on_entity_detail_pane_resource_selected(EntityDetailPane.ResourceSelected(detail, target))
                await pilot.pause()

                body = detail.query_one("#entity_detail_body")
                self.assertIn("test_connection_migration.py", str(body.content))
        finally:
            temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
