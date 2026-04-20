from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

from ssot_tui.actions import ActionDefinition, ActionRegistry
from ssot_tui.persistence import SessionStore
from ssot_tui.presentations import build_detail_view_model, build_section_specs, render_structured_detail
from ssot_tui.providers import BridgeActionProvider, WorkspaceProvider
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

    def test_session_store_defaults_filter_to_null(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        session_root = Path(temp_dir.name) / "session"
        try:
            loaded = SessionStore(session_root).load()
        finally:
            temp_dir.cleanup()

        self.assertIsNone(loaded.filter_text)

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

    def test_workspace_provider_prefers_nearest_ancestor_registry_over_outer_workspace(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        repo = Path(temp_dir.name) / "repo"
        nested_repo = repo / "nested" / "child"
        try:
            (repo / ".git").mkdir()
            (nested_repo / ".ssot").mkdir(parents=True)
            (nested_repo / ".ssot" / "registry.json").write_text("{}", encoding="utf-8")
            candidate = nested_repo / "deeper" / "workspace"
            candidate.mkdir(parents=True)
            resolved = WorkspaceProvider().resolve_preferred_repo(candidate)
        finally:
            temp_dir.cleanup()

        self.assertEqual(resolved, repo.as_posix())

    def test_workspace_provider_falls_back_to_shallowest_descendant_registry(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        root = Path(temp_dir.name)
        outer = root / "workspace"
        repo = outer / "project"
        try:
            (outer / ".git").mkdir(parents=True)
            repo.mkdir(parents=True)
            fixture = temp_repo_from_fixture("repo_valid")
            fixture_repo = Path(fixture.name) / "repo"
            (repo / ".ssot").mkdir(parents=True)
            (repo / ".ssot" / "registry.json").write_text((fixture_repo / ".ssot" / "registry.json").read_text(encoding="utf-8"), encoding="utf-8")
            resolved = WorkspaceProvider().resolve_preferred_repo(outer)
        finally:
            fixture.cleanup()
            temp_dir.cleanup()

        self.assertEqual(resolved, repo.as_posix())

    def test_session_store_returns_none_when_no_registry_exists(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        empty_root = Path(temp_dir.name) / "empty"
        empty_root.mkdir(parents=True)
        (empty_root / ".git").mkdir()
        try:
            store = SessionStore(Path(temp_dir.name) / "session")
            resolved = store.resolve_startup_path(empty_root, SessionState())
        finally:
            temp_dir.cleanup()

        self.assertIsNone(resolved)

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

    def test_workspace_service_keeps_document_rows_as_registry_rows(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        repo = Path(temp_dir.name) / "repo"
        try:
            workspace = RegistryWorkspaceService().load_workspace(repo)
        finally:
            temp_dir.cleanup()

        adr = next(row for row in workspace.collections["adrs"] if row["id"] == "adr:0600")
        self.assertNotIn("body", adr)
        self.assertNotIn("summary", adr)

    def test_workspace_service_exposes_registry_and_schema_versions(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        repo = Path(temp_dir.name) / "repo"
        try:
            workspace = RegistryWorkspaceService().load_workspace(repo)
        finally:
            temp_dir.cleanup()

        self.assertEqual(workspace.registry_version, "0.2.2")
        self.assertEqual(workspace.registry_schema_version, "0.1.0")

    def test_bridge_preview_cli_get_for_document_returns_row_only(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        repo = Path(temp_dir.name) / "repo"
        try:
            preview = BridgeActionProvider().preview_cli_read(repo, "adrs", "adr:0600")
        finally:
            temp_dir.cleanup()

        self.assertIn("\"id\": \"adr:0600\"", preview)
        self.assertNotIn("\"payload\"", preview)
        self.assertNotIn("\"body\"", preview)

    def test_document_detail_renders_multiline_body(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        repo = Path(temp_dir.name) / "repo"
        try:
            workspace = RegistryWorkspaceService().load_workspace(repo)
            specs = build_section_specs(ENTITY_SECTIONS)
            entity_index = {}
            for section, rows in workspace.collections.items():
                for row in rows:
                    entity_id = row.get("id")
                    if isinstance(entity_id, str):
                        entity_index[entity_id] = (section, row)
            adr = next(row for row in workspace.collections["adrs"] if row["id"] == "adr:0609")
            detail = RegistryWorkspaceService().build_detail_entity(workspace.root_path, "adrs", adr)
            view_model = build_detail_view_model(
                detail,
                specs["adrs"],
                workspace_root=workspace.root_path,
                entity_index=entity_index,
                raw_entity=adr,
            )
        finally:
            temp_dir.cleanup()

        rendered = render_structured_detail(view_model)
        self.assertIn("- Body:", rendered)
        self.assertIn("Generated projections include", rendered)
        self.assertNotIn('"body"', view_model.raw_json)


@unittest.skipUnless(BrowserScreen is not None, "textual is not installed")
class TuiOverhaulInteractionTests(unittest.IsolatedAsyncioTestCase):
    async def test_unset_filter_leaves_rows_unfiltered(self) -> None:
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
                self.assertIsNone(screen.state_store.state.session.filter_text)
                self.assertEqual(screen.query_one("#filter_input").value, "")
                self.assertEqual(table.row_count, len(screen.workspace.collections["features"]))
        finally:
            temp_dir.cleanup()

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

    async def test_action_activate_selection_shows_current_entity(self) -> None:
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
                table.focus()
                screen.action_activate_selection()
                await pilot.pause()
                body = screen.query_one("#entity_detail_body")
                self.assertIn("Badges", str(body.content))
        finally:
            temp_dir.cleanup()

    async def test_same_entity_highlight_does_not_rewrite_session(self) -> None:
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
                entity = next(row for row in screen.workspace.collections["features"] if row["id"] == "feat:rfc.9000.connection-migration")
                screen._show_entity(entity)
                await pilot.pause()
                with patch.object(screen.state_store, "update_session", wraps=screen.state_store.update_session) as update_session:
                    screen._show_entity(entity)
                    await pilot.pause()
                update_session.assert_not_called()
        finally:
            temp_dir.cleanup()

    async def test_highlighting_new_entity_does_not_emit_session_rerender(self) -> None:
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
                section, rows = next((name, items) for name, items in screen.workspace.collections.items() if len(items) > 1)
                screen._select_section(section)
                await pilot.pause()
                entity = rows[1]
                with patch.object(screen.state_store, "emit", wraps=screen.state_store.emit) as emit:
                    screen._show_entity(entity)
                    await pilot.pause()
                emit.assert_not_called()
                self.assertEqual(screen.state_store.state.session.selected_entity_id, entity["id"])
        finally:
            temp_dir.cleanup()

    async def test_browser_can_switch_to_document_sections_with_visible_rows(self) -> None:
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

                screen._select_section("adrs")
                await pilot.pause()
                self.assertEqual(screen.active_section, "adrs")
                self.assertGreater(table.row_count, 0)
                adr = table.entity_for_row_index(table.cursor_row)
                self.assertIsNotNone(adr)
                self.assertTrue(adr["id"].startswith("adr:"))

                screen._select_section("specs")
                await pilot.pause()
                self.assertEqual(screen.active_section, "specs")
                self.assertGreater(table.row_count, 0)
                spec = table.entity_for_row_index(table.cursor_row)
                self.assertIsNotNone(spec)
                self.assertTrue(spec["id"].startswith("spc:"))
        finally:
            temp_dir.cleanup()

    async def test_startup_panel_no_longer_renders_recent_repo_selector(self) -> None:
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
                self.assertEqual(screen := app.screen, app.screen)
                self.assertEqual(len(screen.query("#recent_repos")), 0)
        finally:
            temp_dir.cleanup()

    async def test_summary_row_shows_registry_and_schema_versions(self) -> None:
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
                workspace_status = screen.query_one("#workspace_status")
                rendered = str(workspace_status.render())
                self.assertIn(
                    f"ssot-registry: {screen.workspace.registry_version}",
                    rendered,
                )
                self.assertIn(
                    f"schema: {screen.workspace.registry_schema_version}",
                    rendered,
                )
        finally:
            temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
