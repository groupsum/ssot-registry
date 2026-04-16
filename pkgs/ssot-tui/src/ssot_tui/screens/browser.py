from __future__ import annotations

from pathlib import Path
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Input, Static

from ssot_tui.services import ENTITY_SECTIONS, RegistryWorkspace, RegistryWorkspaceService
from ssot_tui.widgets import EntityDetailPane, EntityTable, SectionNavigation


class BrowserScreen(Screen[None]):
    BINDINGS = [
        ("r", "reload_workspace", "Reload"),
        ("v", "validate_workspace", "Validate"),
    ]

    def __init__(self, service: RegistryWorkspaceService | None = None) -> None:
        super().__init__()
        self.service = service or RegistryWorkspaceService()
        self.workspace: RegistryWorkspace | None = None
        self.active_section = ENTITY_SECTIONS[0][0]

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Repository root or .ssot/registry.json", id="repo_path")
        yield Static("Open a repo path and press Enter.", id="status")
        with Horizontal(id="browser"):
            yield SectionNavigation()
            yield EntityTable(id="entity_table")
            yield EntityDetailPane("No entity selected.", id="detail_pane")

    def _rows_for_active_section(self) -> list[dict[str, Any]]:
        if self.workspace is None:
            return []
        return self.workspace.collections.get(self.active_section, [])

    def _refresh_table(self) -> None:
        table = self.query_one(EntityTable)
        table.load_rows(self.active_section, self._rows_for_active_section())
        detail = self.query_one(EntityDetailPane)
        detail.show_entity(None)

    def action_reload_workspace(self) -> None:
        path = self.query_one("#repo_path", Input).value.strip()
        if not path:
            self.query_one("#status", Static).update("Enter a repository path to load.")
            return
        self.workspace = self.service.load_workspace(Path(path))
        self.query_one("#status", Static).update(
            f"Loaded {self.workspace.repo.get('id', '<unknown repo>')} from {self.workspace.root_path}"
        )
        self._refresh_table()

    def action_validate_workspace(self) -> None:
        if self.workspace is None:
            self.query_one("#status", Static).update("Load a repository before validating.")
            return
        validation = self.service.load_workspace(self.workspace.root_path).validation
        failures = validation.get("failures", [])
        if failures:
            self.query_one("#status", Static).update(f"Validation failed: {failures[0]}")
            return
        self.query_one("#status", Static).update("Validation passed.")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "repo_path":
            self.action_reload_workspace()

    def on_tree_node_selected(self, event: SectionNavigation.NodeSelected[str]) -> None:
        if event.node.data is None:
            return
        self.active_section = event.node.data
        self._refresh_table()

    def on_data_table_row_highlighted(self, event: EntityTable.RowHighlighted) -> None:
        rows = self._rows_for_active_section()
        if event.cursor_row < 0 or event.cursor_row >= len(rows):
            return
        self.query_one(EntityDetailPane).show_entity(rows[event.cursor_row])
