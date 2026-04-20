from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Callable

from ssot_tui.services import RegistryWorkspace


STATE_SCHEMA_VERSION = 1


@dataclass(slots=True)
class SessionState:
    schema_version: int = STATE_SCHEMA_VERSION
    last_repo_path: str | None = None
    recent_repos: list[str] = field(default_factory=list)
    active_section: str = "features"
    selected_entity_id: str | None = None
    filter_text: str | None = None
    pane_mode: str = "structured"
    table_mode: str = "fit"
    selected_columns: dict[str, list[str]] = field(default_factory=dict)


@dataclass(slots=True)
class ValidationSummary:
    passed: bool = False
    failure_count: int = 0
    warning_count: int = 0
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    last_checked_label: str = "Never"
    section_failures: dict[str, int] = field(default_factory=dict)


@dataclass(slots=True)
class StatusEntry:
    message: str
    level: str = "info"


@dataclass(slots=True)
class AppState:
    session: SessionState = field(default_factory=SessionState)
    workspace: RegistryWorkspace | None = None
    validation: ValidationSummary = field(default_factory=ValidationSummary)
    status_history: list[StatusEntry] = field(default_factory=list)
    startup_message: str = "Load a repository to start browsing."
    command_palette_open: bool = False
    help_open: bool = False
    filter_focus_requested: bool = False


Subscriber = Callable[[AppState], None]


class AppStateStore:
    def __init__(self, state: AppState | None = None) -> None:
        self._state = state or AppState()
        self._subscribers: list[Subscriber] = []

    @property
    def state(self) -> AppState:
        return self._state

    def subscribe(self, callback: Subscriber) -> None:
        self._subscribers.append(callback)

    def emit(self) -> None:
        for callback in list(self._subscribers):
            callback(self._state)

    def update_session(self, *, emit: bool = True, **changes: object) -> None:
        if not changes:
            return
        current = self._state.session
        if all(getattr(current, key) == value for key, value in changes.items()):
            return
        self._state.session = replace(self._state.session, **changes)
        if emit:
            self.emit()

    def set_workspace(self, workspace: RegistryWorkspace | None, validation: ValidationSummary) -> None:
        self._state.workspace = workspace
        self._state.validation = validation
        self.emit()

    def push_status(self, message: str, level: str = "info") -> None:
        history = [*self._state.status_history, StatusEntry(message=message, level=level)]
        self._state.status_history = history[-8:]
        self.emit()

    def set_overlay_state(self, *, command_palette_open: bool | None = None, help_open: bool | None = None) -> None:
        if command_palette_open is not None:
            self._state.command_palette_open = command_palette_open
        if help_open is not None:
            self._state.help_open = help_open
        self.emit()

    def request_filter_focus(self) -> None:
        self._state.filter_focus_requested = True
        self.emit()

    def clear_filter_focus_request(self) -> None:
        if self._state.filter_focus_requested:
            self._state.filter_focus_requested = False
            self.emit()
