from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Input, Static
from textual.worker import Worker, WorkerState

from ssot_tui.actions import ActionDefinition, ActionRegistry
from ssot_tui.persistence import SessionStore
from ssot_tui.presentations import (
    SectionPresentationSpec,
    build_detail_view_model,
    build_row_view_models,
    build_section_specs,
)
from ssot_tui.providers import BridgeActionProvider, WorkspaceProvider
from ssot_tui.services import ENTITY_SECTIONS, RegistryWorkspace, RegistryWorkspaceService
from ssot_tui.state import AppState, AppStateStore, ValidationSummary
from ssot_tui.widgets import CommandPaletteScreen, EntityDetailPane, EntityTable, HelpScreen, SectionNavigation, StatusCenter


@dataclass(slots=True)
class WorkspaceLoadResult:
    request_id: int
    requested_path: str
    workspace: RegistryWorkspace
    validation: ValidationSummary


class BrowserScreen(Screen[None]):
    BINDINGS = [
        ("r", "reload_workspace", "Reload"),
        ("v", "validate_workspace", "Validate"),
        ("/", "focus_filter", "Filter"),
        ("ctrl+p", "show_palette", "Palette"),
        ("?", "show_help", "Help"),
        ("tab", "cycle_focus", "Next Pane"),
        ("shift+tab", "cycle_focus_reverse", "Prev Pane"),
        ("j", "move_down", "Down"),
        ("k", "move_up", "Up"),
        ("h", "focus_sections", "Sections"),
        ("l", "focus_table", "Table"),
        ("enter", "activate_selection", "Open"),
        ("escape", "escape_mode", "Escape"),
        ("t", "toggle_detail_mode", "Raw/Structured"),
        ("m", "cycle_table_mode", "Table Mode"),
    ]

    def __init__(
        self,
        service: RegistryWorkspaceService | None = None,
        initial_path: str | Path | None = None,
        session_store: SessionStore | None = None,
        workspace_provider: WorkspaceProvider | None = None,
        bridge_provider: BridgeActionProvider | None = None,
    ) -> None:
        super().__init__()
        self.service = service or RegistryWorkspaceService()
        self.workspace_provider = workspace_provider or WorkspaceProvider()
        self.session_store = session_store or SessionStore(workspace_provider=self.workspace_provider)
        session = self.session_store.load()
        self.state_store = AppStateStore(AppState(session=session))
        self.bridge_provider = bridge_provider or BridgeActionProvider()
        self.workspace: RegistryWorkspace | None = None
        self.active_section = session.active_section or ENTITY_SECTIONS[0][0]
        self.initial_path = Path(initial_path) if initial_path is not None else None
        self._launch_cwd = Path.cwd().resolve()
        self._current_detail_entity_id: str | None = None
        self._detail_view_model = None
        self._last_filtered_count = 0
        self._last_navigation_signature: tuple[tuple[tuple[str, int], ...], tuple[tuple[str, int], ...]] | None = None
        self._load_request_id = 0
        self._active_load_worker: Worker[WorkspaceLoadResult] | None = None
        self._active_load_path: str | None = None
        self.section_specs: dict[str, SectionPresentationSpec] = build_section_specs(ENTITY_SECTIONS)
        self.action_registry = ActionRegistry()

    def compose(self) -> ComposeResult:
        with Vertical(id="startup_panel"):
            yield Static("Resolve a repo from the current directory or enter a path.", id="startup_message")
            yield Input(placeholder="Repository root or .ssot/registry.json", id="repo_path")
        yield Input(placeholder="Filter current section", id="filter_input")
        with Horizontal(id="browser"):
            yield SectionNavigation(id="section_nav")
            yield EntityTable(id="entity_table")
            yield EntityDetailPane("No entity selected.", id="detail_pane")
        with Horizontal(id="summary_row"):
            yield Static("No workspace loaded.", id="summary_status")
            yield Static("Repo: n/a | Registry: n/a", id="workspace_status")
            yield Static("Validation: n/a", id="validation_status")
        yield StatusCenter(id="status_center")

    def on_mount(self) -> None:
        self.state_store.subscribe(self._render_state)
        self._register_actions()
        self.query_one(SectionNavigation).load_sections(ENTITY_SECTIONS)
        self.query_one("#filter_input", Input).value = self.state_store.state.session.filter_text or ""
        startup_path = self._startup_path()
        if startup_path is not None:
            self.query_one("#repo_path", Input).value = startup_path
            self.action_reload_workspace()
        else:
            self._set_startup_message("No repo auto-detected. Enter a path.")
            self.query_one("#repo_path", Input).focus()
        self._render_state(self.state_store.state)

    def _startup_path(self) -> str | None:
        if self.initial_path is not None:
            try:
                return self.workspace_provider.resolve_startup_repo(self.initial_path)
            except FileNotFoundError:
                return None
        return self.session_store.resolve_startup_path(self._launch_cwd, self.state_store.state.session)

    def _format_loaded_path_display(self, path: str | Path) -> str:
        candidate = Path(path).expanduser().resolve()
        try:
            relative = candidate.relative_to(self._launch_cwd)
        except ValueError:
            return "."
        relative_text = relative.as_posix()
        return "." if relative_text in {"", "."} else relative_text

    def _register_actions(self) -> None:
        register = self.action_registry.register
        register(self._action("reload", "Reload workspace", "Reload the current repo from disk.", "r", "workspace", self.action_reload_workspace, self._has_path))
        register(self._action("validate", "Validate workspace", "Re-run validation and refresh counts.", "v", "workspace", self.action_validate_workspace, self._has_workspace))
        register(self._action("focus_filter", "Focus filter", "Jump to the inline section filter.", "/", "navigation", self.action_focus_filter, self._has_workspace))
        register(self._action("toggle_detail", "Toggle raw detail", "Switch the detail pane between structured and raw JSON.", "t", "view", self.action_toggle_detail_mode, self._has_selected_entity))
        register(self._action("table_mode", "Cycle table mode", "Switch between fit, wrap, and wide table presets.", "m", "view", self.action_cycle_table_mode, self._has_workspace))
        register(self._action("copy_id", "Copy entity id", "Copy the selected entity id to the clipboard.", None, "entity", self._copy_selected_entity_id, self._has_selected_entity))
        register(self._action("copy_path", "Copy source path", "Copy the selected entity path when present.", None, "entity", self._copy_selected_entity_path, self._selected_entity_has_path))
        register(self._action("preview_cli_get", "Preview CLI get", "Render the safe CLI get preview for the selected entity.", None, "bridge", self._preview_cli_get, self._has_selected_entity))
        register(self._action("preview_cli_list", "Preview CLI list", "Render the safe CLI list preview for the active section.", None, "bridge", self._preview_cli_list, self._has_workspace))
        register(self._action("open_repo", "Open repo root", "Launch the current repo in the platform file browser.", None, "bridge", self._open_repo_root, self._has_workspace))
        register(self._action("open_registry", "Open registry file", "Launch the current registry.json file.", None, "bridge", self._open_registry_file, self._has_workspace))
        register(self._action("reveal_source", "Reveal source path", "Reveal the selected entity file when one is known.", None, "bridge", self._reveal_selected_path, self._selected_entity_has_path))
        register(self._action("show_help", "Show help", "Open the keyboard and actions help overlay.", "?", "system", self.action_show_help, lambda: True))
        register(self._action("show_palette", "Show palette", "Open the command palette.", "ctrl+p", "system", self.action_show_palette, lambda: True))

    def _action(
        self,
        action_id: str,
        label: str,
        description: str,
        keybinding: str | None,
        scope: str,
        handler: callable,
        enabled: callable,
    ) -> ActionDefinition:
        return ActionDefinition(action_id, label, description, keybinding, scope, handler, enabled)

    def _render_state(self, state: AppState) -> None:
        self.workspace = state.workspace
        self.active_section = state.session.active_section
        self.query_one(StatusCenter).show_messages([entry.message for entry in state.status_history])
        self._update_summary()
        if self.workspace is None:
            self.query_one(EntityTable).load_rows(["id", "title", "status"], [])
            self.query_one(EntityDetailPane).show_entity(None)
            self._last_navigation_signature = None
            return
        self._refresh_navigation(state.validation.section_failures)
        self._refresh_table(selected_entity_id=state.session.selected_entity_id)
        if state.filter_focus_requested:
            self.query_one("#filter_input", Input).focus()
            self.state_store.clear_filter_focus_request()

    def _refresh_navigation(self, failures: dict[str, int]) -> None:
        if self.workspace is None:
            self._last_navigation_signature = None
            return
        counts = self.service.section_counts(self.workspace)
        signature = (tuple(sorted(counts.items())), tuple(sorted(failures.items())))
        if self._last_navigation_signature == signature:
            return
        self._last_navigation_signature = signature
        self.query_one(SectionNavigation).load_sections(
            ENTITY_SECTIONS,
            counts=counts,
            failures=failures,
        )

    def _set_startup_message(self, message: str) -> None:
        self.query_one("#startup_message", Static).update(message)

    def _rows_for_active_section(self) -> list[dict[str, Any]]:
        if self.workspace is None:
            return []
        return self.workspace.collections.get(self.active_section, [])

    def _filtered_rows(self) -> list[dict[str, Any]]:
        rows = self._rows_for_active_section()
        filter_text = self.state_store.state.session.filter_text
        if filter_text is None:
            return rows
        needle = filter_text.strip().lower()
        if not needle:
            return rows
        return [row for row in rows if needle in json.dumps(row, sort_keys=True).lower()]

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

    def _columns_for_section(self, rows: list[dict[str, Any]]) -> list[str]:
        spec = self.section_specs[self.active_section]
        selected = self.state_store.state.session.selected_columns.get(self.active_section)
        if selected:
            return self._with_path_column(selected, rows, max_columns=None)
        if self.state_store.state.session.table_mode == "wide":
            extras: list[str] = []
            for row in rows:
                for key in row.keys():
                    if key not in spec.preferred_columns and key not in extras:
                        extras.append(key)
            columns = list(spec.preferred_columns) + extras[:3]
            return self._with_path_column(columns, rows, max_columns=None)
        if self.state_store.state.session.table_mode == "wrap":
            columns = list(spec.preferred_columns[: min(4, len(spec.preferred_columns))])
            return self._with_path_column(columns, rows, max_columns=4)
        return self._with_path_column(list(spec.preferred_columns), rows, max_columns=None)

    def _with_path_column(self, columns: list[str], rows: list[dict[str, Any]], *, max_columns: int | None) -> list[str]:
        has_path_values = any(isinstance(row.get("path"), str) and bool(row.get("path")) for row in rows)
        if not has_path_values:
            return columns
        if "path" in columns:
            return columns
        if max_columns is not None and len(columns) >= max_columns:
            return [*columns[: max_columns - 1], "path"]
        return [*columns, "path"]

    def _refresh_table(self, *, selected_entity_id: str | None = None) -> None:
        table = self.query_one(EntityTable)
        rows = self._filtered_rows()
        columns = self._columns_for_section(rows)
        reloaded = table.load_rows(columns, build_row_view_models(columns, rows))
        self._last_filtered_count = len(rows)
        if not rows:
            self._current_detail_entity_id = None
            self._detail_view_model = None
            self.query_one(EntityDetailPane).show_entity(None)
            self._update_summary()
            return
        row_index = 0
        if selected_entity_id is not None:
            selected_index = table.row_index_for_entity_id(selected_entity_id)
            if selected_index is not None:
                row_index = selected_index
        if reloaded or table.cursor_row != row_index:
            table.move_cursor(row=row_index, column=0, animate=False, scroll=False)
        entity = rows[row_index]
        if self._current_detail_entity_id != str(entity.get("id", "")) or reloaded:
            self._show_entity(entity)
        self._update_summary()

    def _show_entity(self, entity: dict[str, Any] | None) -> None:
        if entity is None or self.workspace is None:
            self._current_detail_entity_id = None
            self._detail_view_model = None
            self.query_one(EntityDetailPane).show_entity(None)
            return
        self._current_detail_entity_id = str(entity.get("id", ""))
        detail_entity = self.service.build_detail_entity(self.workspace.root_path, self.active_section, entity)
        self._detail_view_model = build_detail_view_model(
            detail_entity,
            self.section_specs[self.active_section],
            workspace_root=self.workspace.root_path,
            entity_index=self._entity_index(),
            raw_entity=entity,
        )
        raw_mode = self.state_store.state.session.pane_mode == "raw"
        self.query_one(EntityDetailPane).show_view_model(self._detail_view_model, raw_mode=raw_mode)
        if self.state_store.state.session.selected_entity_id != self._current_detail_entity_id:
            # Row highlighting fires during keyboard navigation. Persisting the
            # selected entity without emitting prevents the table from being
            # re-rendered while the cursor is moving.
            self._persist_session(selected_entity_id=self._current_detail_entity_id, emit=False)

    def _select_entity_id(self, entity_id: str) -> None:
        if self.workspace is None:
            return
        target = self._entity_index().get(entity_id)
        if target is None:
            self._push_status(f"Unable to traverse to {entity_id}; it is not present in the loaded workspace.", level="warning")
            return
        section, row = target
        self.active_section = section
        self._persist_session(active_section=section, selected_entity_id=entity_id)
        self._refresh_table(selected_entity_id=entity_id)
        label = row.get("title") or row.get("version") or entity_id
        self._push_status(f"Selected {entity_id} in {section}: {label}")

    def _select_section(
        self,
        section: str,
        *,
        selected_entity_id: str | None = None,
        announce: bool = False,
    ) -> None:
        if self.workspace is None:
            return
        if section not in self.workspace.collections:
            self._push_status(f"Unknown section: {section}", level="warning")
            return
        self.active_section = section
        self._persist_session(active_section=section, selected_entity_id=selected_entity_id)
        self._refresh_table(selected_entity_id=selected_entity_id)
        if announce:
            self._push_status(f"Switched to {section} ({len(self.workspace.collections.get(section, []))} rows).")

    def _show_file_resource(self, relative_path: str, absolute_path: str) -> None:
        path = Path(absolute_path)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            self._push_status(f"Resource {relative_path} is not UTF-8 text.", level="warning")
            return
        if len(text) > 8000:
            text = f"{text[:8000]}\n\n... truncated ..."
        self.query_one(EntityDetailPane).show_resource_text(relative_path, text)
        self._push_status(f"Previewing {relative_path}")

    def _update_summary(self) -> None:
        if self.workspace is None:
            self.query_one("#summary_status", Static).update("No workspace loaded.")
            self.query_one("#workspace_status", Static).update("Repo: n/a | Registry: n/a")
            self.query_one("#validation_status", Static).update("Validation: n/a")
            return
        total = len(self._rows_for_active_section())
        filtered = self._last_filtered_count
        repo_id = self.workspace.repo.get("id", "<unknown repo>")
        self.query_one("#summary_status", Static).update(
            f"{repo_id} | {self.active_section} | {filtered}/{total} rows | mode={self.state_store.state.session.table_mode}"
        )
        self.query_one("#workspace_status", Static).update(
            " | ".join(
                [
                    f"Repo: {self._format_loaded_path_display(self.workspace.root_path)}",
                    f"Registry: {self._format_loaded_path_display(self.workspace.registry_path)}",
                    f"ssot-registry: {self.workspace.registry_version}",
                    f"schema: {self.workspace.registry_schema_version}",
                ]
            )
        )
        validation = self.state_store.state.validation
        status = "passed" if validation.passed else f"{validation.failure_count} failures"
        self.query_one("#validation_status", Static).update(
            f"Validation: {status}; warnings={validation.warning_count}; checked={validation.last_checked_label}"
        )
        self._set_startup_message(
            "Loaded repo root: "
            f"{self._format_loaded_path_display(self.workspace.root_path)}\n"
            "Loaded registry: "
            f"{self._format_loaded_path_display(self.workspace.registry_path)}"
        )

    def _persist_session(self, *, emit: bool = True, **changes: object) -> None:
        session = self.state_store.state.session
        next_recent = session.recent_repos
        if "last_repo_path" in changes and isinstance(changes["last_repo_path"], str):
            last_repo_path = changes["last_repo_path"]
            next_recent = [last_repo_path, *[repo for repo in session.recent_repos if repo != last_repo_path]][:8]
            changes["recent_repos"] = next_recent
        self.state_store.update_session(emit=emit, **changes)
        self.session_store.save(self.state_store.state.session)

    def _push_status(self, message: str, level: str = "info") -> None:
        self.state_store.push_status(message, level=level)

    def _format_load_error(self, path: str, exc: Exception) -> str:
        if isinstance(exc, FileNotFoundError):
            return f"Registry not found for {path}. Point at a repo root, .ssot directory, registry.json file, or nested path inside the repo."
        if isinstance(exc, json.JSONDecodeError):
            return f"Registry JSON is invalid at {path}: line {exc.lineno}, column {exc.colno}."
        return f"Unable to load registry from {path}: {exc}"

    def action_reload_workspace(self) -> None:
        path = self.query_one("#repo_path", Input).value.strip()
        if not path:
            self._push_status("Enter a repository path to load.", level="warning")
            return
        if self._active_load_worker is not None:
            self._active_load_worker.cancel()
        self._load_request_id += 1
        self._active_load_path = path
        self._set_startup_message(f"Loading registry from {path} in the background...")
        self._push_status(f"Loading registry from {path} in the background.")
        self._active_load_worker = self._load_workspace_background(self._load_request_id, path)

    @work(name="workspace_load", group="workspace_load", exclusive=True, exit_on_error=False, thread=True)
    def _load_workspace_background(self, request_id: int, path: str) -> WorkspaceLoadResult:
        registry_path = self.workspace_provider.resolve_preferred_registry_path(Path(path))
        workspace = self.service.load_workspace(registry_path)
        validation = self.workspace_provider.build_validation_summary(workspace.validation)
        return WorkspaceLoadResult(
            request_id=request_id,
            requested_path=path,
            workspace=workspace,
            validation=validation,
        )

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker is not self._active_load_worker:
            return
        if event.state == WorkerState.CANCELLED:
            self._active_load_worker = None
            self._active_load_path = None
            return
        if event.state == WorkerState.ERROR:
            path = self._active_load_path or "requested path"
            self._active_load_worker = None
            self._active_load_path = None
            error = event.worker.error or RuntimeError("unknown worker failure")
            self._push_status(self._format_load_error(path, error), level="error")
            return
        if event.state != WorkerState.SUCCESS:
            return

        result = event.worker.result
        self._active_load_worker = None
        self._active_load_path = None
        if result is None or result.request_id != self._load_request_id:
            return

        workspace = result.workspace
        self.state_store.set_workspace(workspace, result.validation)
        self.active_section = self.state_store.state.session.active_section or ENTITY_SECTIONS[0][0]
        self._persist_session(last_repo_path=workspace.root_path, active_section=self.active_section)
        self._push_status(
            "Loaded "
            f"{workspace.repo.get('id', '<unknown repo>')} from "
            f"{self._format_loaded_path_display(workspace.root_path)}"
        )

    def action_validate_workspace(self) -> None:
        if self.workspace is None:
            self._push_status("Load a repository before validating.", level="warning")
            return
        try:
            validation = self.workspace_provider.validate(self.workspace.root_path)
            self.state_store.set_workspace(self.workspace, validation)
        except Exception as exc:
            self._push_status(self._format_load_error(self.workspace.root_path, exc), level="error")
            return
        if validation.failure_count:
            self._push_status(f"Validation failed: {validation.failures[0]}", level="error")
            return
        self._push_status("Validation passed.")

    def action_focus_filter(self) -> None:
        self.state_store.request_filter_focus()

    def action_show_palette(self) -> None:
        actions = self.action_registry.enabled_actions()
        self.push_screen(CommandPaletteScreen(actions), self._run_palette_action)

    def action_show_help(self) -> None:
        self.push_screen(HelpScreen(self.action_registry.enabled_actions()))

    def action_cycle_focus(self) -> None:
        self._cycle_focus(reverse=False)

    def action_cycle_focus_reverse(self) -> None:
        self._cycle_focus(reverse=True)

    def action_move_down(self) -> None:
        focused = self.focused
        if isinstance(focused, EntityTable):
            focused.action_cursor_down()

    def action_move_up(self) -> None:
        focused = self.focused
        if isinstance(focused, EntityTable):
            focused.action_cursor_up()

    def action_focus_sections(self) -> None:
        self.query_one(SectionNavigation).focus()

    def action_focus_table(self) -> None:
        self.query_one(EntityTable).focus()

    def action_activate_selection(self) -> None:
        focused = self.focused
        if isinstance(focused, EntityTable):
            self._show_entity(focused.entity_for_row_index(focused.cursor_row))
            return

    def action_escape_mode(self) -> None:
        filter_input = self.query_one("#filter_input", Input)
        if filter_input.value:
            filter_input.value = ""
            self._persist_session(filter_text=None)
            self._refresh_table(selected_entity_id=self._current_detail_entity_id)
            self._push_status("Cleared filter.")
            return
        self.query_one(EntityTable).focus()

    def action_toggle_detail_mode(self) -> None:
        next_mode = "raw" if self.state_store.state.session.pane_mode == "structured" else "structured"
        self._persist_session(pane_mode=next_mode)
        if self._detail_view_model is not None:
            self.query_one(EntityDetailPane).toggle_raw_mode(raw_mode=next_mode == "raw", view_model=self._detail_view_model)
        self._push_status(f"Detail pane switched to {next_mode}.")

    def action_cycle_table_mode(self) -> None:
        modes = ["fit", "wrap", "wide"]
        current = self.state_store.state.session.table_mode
        next_mode = modes[(modes.index(current) + 1) % len(modes)]
        self._persist_session(table_mode=next_mode)
        self._refresh_table(selected_entity_id=self._current_detail_entity_id)
        self._push_status(f"Table mode switched to {next_mode}.")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "repo_path":
            self.action_reload_workspace()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "filter_input":
            self._persist_session(filter_text=event.value or None)
            self._refresh_table(selected_entity_id=self._current_detail_entity_id)

    def on_tree_node_selected(self, event: SectionNavigation.NodeSelected[str]) -> None:
        if event.node.data is None:
            return
        self._select_section(event.node.data)

    def on_data_table_row_highlighted(self, event: EntityTable.RowHighlighted) -> None:
        self._show_entity(self.query_one(EntityTable).entity_for_row_index(event.cursor_row))

    def on_data_table_row_selected(self, event: EntityTable.RowSelected) -> None:
        self._show_entity(self.query_one(EntityTable).entity_for_row_index(event.cursor_row))

    def on_data_table_cell_selected(self, event: EntityTable.CellSelected) -> None:
        self._show_entity(self.query_one(EntityTable).entity_for_row_index(event.coordinate.row))

    def on_data_table_cell_highlighted(self, event: EntityTable.CellHighlighted) -> None:
        self._show_entity(self.query_one(EntityTable).entity_for_row_index(event.coordinate.row))

    def on_entity_detail_pane_resource_selected(self, event: EntityDetailPane.ResourceSelected) -> None:
        if event.target.kind == "entity":
            self._select_entity_id(event.target.value)
            return
        if event.target.kind == "file" and event.target.absolute_path is not None:
            self._show_file_resource(event.target.value, event.target.absolute_path)

    def _cycle_focus(self, *, reverse: bool) -> None:
        widgets = [
            self.query_one("#repo_path", Input),
            self.query_one("#filter_input", Input),
            self.query_one(SectionNavigation),
            self.query_one(EntityTable),
            self.query_one(EntityDetailPane),
        ]
        current = self.focused
        try:
            index = widgets.index(current)
        except ValueError:
            index = 0
        next_index = (index - 1) % len(widgets) if reverse else (index + 1) % len(widgets)
        widgets[next_index].focus()

    def _run_palette_action(self, action_id: str | None) -> None:
        if not action_id or action_id == "command_palette_empty":
            return
        self.action_registry.get(action_id).handler()

    def _copy_text(self, text: str, label: str) -> None:
        copier = getattr(self.app, "copy_to_clipboard", None)
        if callable(copier):
            copier(text)
            self._push_status(f"Copied {label} to clipboard.")
            return
        self._push_status(f"Clipboard unavailable; {label}: {text}", level="warning")

    def _copy_selected_entity_id(self) -> None:
        if self._current_detail_entity_id is not None:
            self._copy_text(self._current_detail_entity_id, "entity id")

    def _copy_selected_entity_path(self) -> None:
        entity = self._selected_entity()
        if entity is None:
            return
        path = entity.get("path")
        if isinstance(path, str):
            self._copy_text(path, "entity path")

    def _preview_cli_get(self) -> None:
        if self.workspace is None or self._current_detail_entity_id is None:
            return
        text = self.bridge_provider.preview_cli_read(self.workspace.root_path, self.active_section, self._current_detail_entity_id)
        self.query_one(EntityDetailPane).show_resource_text(f"CLI preview: {self._current_detail_entity_id}", text)
        self._push_status(f"Previewed CLI get for {self._current_detail_entity_id}.")

    def _preview_cli_list(self) -> None:
        if self.workspace is None:
            return
        text = self.bridge_provider.preview_cli_read(self.workspace.root_path, self.active_section)
        self.query_one(EntityDetailPane).show_resource_text(f"CLI preview: {self.active_section} list", text)
        self._push_status(f"Previewed CLI list for {self.active_section}.")

    def _open_repo_root(self) -> None:
        if self.workspace is None:
            return
        self._run_bridge_command(self.bridge_provider.build_open_path_command(self.workspace.root_path))

    def _open_registry_file(self) -> None:
        if self.workspace is None:
            return
        self._run_bridge_command(self.bridge_provider.build_open_path_command(self.workspace.registry_path))

    def _reveal_selected_path(self) -> None:
        entity = self._selected_entity()
        if entity is None or self.workspace is None:
            return
        path = entity.get("path")
        if isinstance(path, str):
            self._run_bridge_command(self.bridge_provider.build_reveal_path_command(Path(self.workspace.root_path) / path))

    def _run_bridge_command(self, bridge_command) -> None:
        result = self.bridge_provider.run(bridge_command)
        if result.returncode == 0:
            self._push_status(f"Ran {bridge_command.label}: {' '.join(bridge_command.command)}")
            return
        self._push_status(
            f"Bridge action failed for {bridge_command.label}: {result.stderr.strip() or result.stdout.strip() or result.returncode}",
            level="error",
        )

    def _selected_entity(self) -> dict[str, Any] | None:
        if self._current_detail_entity_id is None or self.workspace is None:
            return None
        target = self._entity_index().get(self._current_detail_entity_id)
        return None if target is None else target[1]

    def _has_path(self) -> bool:
        return bool(self.query_one("#repo_path", Input).value.strip())

    def _has_workspace(self) -> bool:
        return self.workspace is not None

    def _has_selected_entity(self) -> bool:
        return self._current_detail_entity_id is not None

    def _selected_entity_has_path(self) -> bool:
        entity = self._selected_entity()
        return bool(isinstance(entity, dict) and isinstance(entity.get("path"), str))
