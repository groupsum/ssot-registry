from __future__ import annotations

import json
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

    def __init__(self, service: RegistryWorkspaceService | None = None, initial_path: str | Path | None = None) -> None:
        super().__init__()
        self.service = service or RegistryWorkspaceService()
        self.workspace: RegistryWorkspace | None = None
        self.active_section = ENTITY_SECTIONS[0][0]
        self.initial_path = Path(initial_path) if initial_path is not None else Path.cwd()

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Repository root or .ssot/registry.json", id="repo_path")
        yield Static("Open a repo path and press Enter.", id="status")
        with Horizontal(id="browser"):
            yield SectionNavigation()
            yield EntityTable(id="entity_table")
            yield EntityDetailPane("No entity selected.", id="detail_pane")

    def on_mount(self) -> None:
        path_input = self.query_one("#repo_path", Input)
        path_input.value = self.initial_path.as_posix()
        self.action_reload_workspace()

    def _rows_for_active_section(self) -> list[dict[str, Any]]:
        if self.workspace is None:
            return []
        return self.workspace.collections.get(self.active_section, [])

    def _entity_index(self) -> dict[str, tuple[str, dict[str, Any]]]:
        if self.workspace is None:
            return {}
        index: dict[str, tuple[str, dict[str, Any]]] = {}
        for section, rows in self.workspace.collections.items():
            for row in rows:
                entity_id = row.get("id")
                if isinstance(entity_id, str):
                    index[entity_id] = (section, row)
        return index

    def _refresh_table(self, *, selected_entity_id: str | None = None) -> None:
        table = self.query_one(EntityTable)
        rows = self._rows_for_active_section()
        table.load_rows(self.active_section, rows)
        detail = self.query_one(EntityDetailPane)
        if not rows:
            detail.show_entity(None)
            return
        row_index = 0
        if selected_entity_id is not None:
            selected_index = table.row_index_for_entity_id(selected_entity_id)
            if selected_index is not None:
                row_index = selected_index
        table.move_cursor(row=row_index, column=0, animate=False, scroll=False)
        self._show_entity(rows[row_index])

    def _set_status(self, message: str) -> None:
        self.query_one("#status", Static).update(message)

    def _format_load_error(self, path: str, exc: Exception) -> str:
        if isinstance(exc, FileNotFoundError):
            return f"Registry not found for {path}. Point at a repo root, .ssot directory, registry.json file, or nested path inside the repo."
        if isinstance(exc, json.JSONDecodeError):
            return f"Registry JSON is invalid at {path}: line {exc.lineno}, column {exc.colno}."
        return f"Unable to load registry from {path}: {exc}"

    def _show_entity(self, entity: dict[str, Any] | None) -> None:
        detail = self.query_one(EntityDetailPane)
        detail.show_entity(
            entity,
            workspace_root=self.workspace.root_path if self.workspace is not None else None,
            entity_index=self._entity_index(),
        )

    def _select_entity_id(self, entity_id: str) -> None:
        if self.workspace is None:
            return
        target = self._entity_index().get(entity_id)
        if target is None:
            self._set_status(f"Unable to traverse to {entity_id}; it is not present in the loaded workspace.")
            return
        section, row = target
        self.active_section = section
        self._refresh_table(selected_entity_id=entity_id)
        label = row.get("title") or row.get("version") or entity_id
        self._set_status(f"Selected {entity_id} in {section}: {label}")

    def _show_file_resource(self, relative_path: str, absolute_path: str) -> None:
        path = Path(absolute_path)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            self._set_status(f"Resource {relative_path} is not UTF-8 text.")
            return
        if len(text) > 8000:
            text = f"{text[:8000]}\n\n... truncated ..."
        self.query_one(EntityDetailPane).show_resource_text(relative_path, text)
        self._set_status(f"Previewing {relative_path}")

    def action_reload_workspace(self) -> None:
        path = self.query_one("#repo_path", Input).value.strip()
        if not path:
            self._set_status("Enter a repository path to load.")
            return
        try:
            self.workspace = self.service.load_workspace(Path(path))
        except Exception as exc:
            self.workspace = None
            self._set_status(self._format_load_error(path, exc))
            self._refresh_table()
            return
        self._set_status(f"Loaded {self.workspace.repo.get('id', '<unknown repo>')} from {self.workspace.root_path}")
        self._refresh_table()

    def action_validate_workspace(self) -> None:
        if self.workspace is None:
            self._set_status("Load a repository before validating.")
            return
        try:
            validation = self.service.load_workspace(self.workspace.root_path).validation
        except Exception as exc:
            self._set_status(self._format_load_error(self.workspace.root_path, exc))
            return
        failures = validation.get("failures", [])
        if failures:
            self._set_status(f"Validation failed: {failures[0]}")
            return
        self._set_status("Validation passed.")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "repo_path":
            self.action_reload_workspace()

    def on_tree_node_selected(self, event: SectionNavigation.NodeSelected[str]) -> None:
        if event.node.data is None:
            return
        self.active_section = event.node.data
        self._refresh_table()

    def on_data_table_row_highlighted(self, event: EntityTable.RowHighlighted) -> None:
        self._show_entity(self.query_one(EntityTable).entity_for_row_index(event.cursor_row))

    def on_data_table_row_selected(self, event: EntityTable.RowSelected) -> None:
        self._show_entity(self.query_one(EntityTable).entity_for_row_index(event.cursor_row))

    def on_entity_detail_pane_resource_selected(self, event: EntityDetailPane.ResourceSelected) -> None:
        if event.target.kind == "entity":
            self._select_entity_id(event.target.value)
            return
        if event.target.kind == "file" and event.target.absolute_path is not None:
            self._show_file_resource(event.target.value, event.target.absolute_path)
