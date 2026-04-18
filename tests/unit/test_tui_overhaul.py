from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

from ssot_tui.actions import ActionDefinition, ActionRegistry
from ssot_tui.persistence import SessionStore
from ssot_tui.presentations import build_detail_view_model, build_section_specs
from ssot_tui.providers import BridgeActionProvider
from ssot_tui.services import ENTITY_SECTIONS, RegistryWorkspaceService
from ssot_tui.state import SessionState
from tests.helpers import temp_repo_from_fixture

if importlib.util.find_spec("textual") is not None:
    from textual.app import App
    from ssot_tui.screens.browser import BrowserScreen
    from ssot_tui.widgets import EntityTable
else:
    BrowserScreen = None


class TuiOverhaulUnitTests(unittest.TestCase):
    def test_session_store_round_trips_versioned_session(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        session_root = Path(temp_dir.name) / "session"
        try:
            store = SessionStore(session_root)
            session = SessionState(
                last_repo_path="E:/repo",
                recent_repos=["E:/repo", "E:/other"],
                active_section="claims",
                selected_entity_id="clm:1",
                filter_text="needle",
                pane_mode="raw",
                table_mode="wide",
                selected_columns={"claims": ["id", "title", "tier"]},
            )
            store.save(session)
            loaded = store.load()
        finally:
            temp_dir.cleanup()

        self.assertEqual(loaded.last_repo_path, "E:/repo")
        self.assertEqual(loaded.recent_repos, ["E:/repo", "E:/other"])
        self.assertEqual(loaded.selected_columns["claims"], ["id", "title", "tier"])

    def test_session_store_prefers_last_valid_repo_then_cwd(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        repo = Path(temp_dir.name) / "repo"
        try:
            store = SessionStore(Path(temp_dir.name) / "session")
            session = SessionState(last_repo_path=repo.as_posix())
            resolved = store.resolve_startup_path(repo / "nested", session)
        finally:
            temp_dir.cleanup()

        self.assertEqual(resolved, repo.as_posix())

    def test_action_registry_filters_disabled_actions(self) -> None:
        registry = ActionRegistry()
        registry.register(ActionDefinition("enabled", "Enabled", "Visible", "e", "scope", lambda: None, lambda: True))
        registry.register(ActionDefinition("disabled", "Disabled", "Hidden", "d", "scope", lambda: None, lambda: False))
        enabled = registry.enabled_actions()
        self.assertEqual([action.id for action in enabled], ["enabled"])

    def test_bridge_action_provider_builds_safe_cli_command(self) -> None:
        provider = BridgeActionProvider()
        command = provider.build_cli_get_command("E:/repo", "features", "feat:demo")
        self.assertEqual(command.command[:4], [command.command[0], "-m", "ssot_cli.main", "feature"])
        self.assertIn("get", command.command)
        self.assertEqual(command.command[-1], "feat:demo")

    def test_detail_view_model_builds_related_entity_and_file_resources(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        repo = Path(temp_dir.name) / "repo"
        try:
            workspace = RegistryWorkspaceService().load_workspace(repo)
            entity_index = {}
            for section, rows in workspace.collections.items():
                for row in rows:
                    entity_id = row.get("id")
                    if isinstance(entity_id, str):
                        entity_index[entity_id] = (section, row)
            specs = build_section_specs(ENTITY_SECTIONS)
            entity = next(row for row in workspace.collections["tests"] if row["id"] == "tst:pytest.rfc.9000.connection-migration")
            view_model = build_detail_view_model(entity, specs["tests"], workspace_root=workspace.root_path, entity_index=entity_index)
        finally:
            temp_dir.cleanup()

        kinds = {resource.kind for resource in view_model.resources}
        self.assertIn("entity", kinds)
        self.assertIn("file", kinds)


@unittest.skipUnless(BrowserScreen is not None, "textual is not installed")
class TuiOverhaulInteractionTests(unittest.IsolatedAsyncioTestCase):
    async def test_filter_updates_visible_rows(self) -> None:
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
                starting_rows = table.row_count
                filter_input = screen.query_one("#filter_input")
                filter_input.value = "definitely-no-match"
                await pilot.pause()
                self.assertLess(table.row_count, starting_rows)
                self.assertEqual(screen.state_store.state.session.filter_text, "definitely-no-match")
        finally:
            temp_dir.cleanup()

    async def test_toggle_detail_mode_switches_body_format(self) -> None:
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
                body = screen.query_one("#entity_detail_body")
                structured = str(body.content)
                screen.action_toggle_detail_mode()
                await pilot.pause()
                raw = str(body.content)
                self.assertIn("Badges", structured)
                self.assertIn('"id": "feat:rfc.9000.connection-migration"', raw)
        finally:
            temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
