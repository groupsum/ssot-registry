from __future__ import annotations

import json
import os
from pathlib import Path

from ssot_registry.util.fs import ensure_directory

from .providers import WorkspaceProvider
from .state import STATE_SCHEMA_VERSION, SessionState


def _default_config_dir() -> Path:
    override = os.environ.get("SSOT_TUI_CONFIG_DIR")
    if override:
        return Path(override).expanduser()
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / "ssot-tui"
    return Path.home() / ".config" / "ssot-tui"


class SessionStore:
    def __init__(self, root: str | Path | None = None, workspace_provider: WorkspaceProvider | None = None) -> None:
        target_root = Path(root or _default_config_dir())
        try:
            self.root = ensure_directory(target_root)
        except PermissionError:
            fallback_root = ensure_directory(Path.cwd() / ".ssot" / "tui-session")
            self.root = fallback_root
        self.path = self.root / "session.json"
        self.workspace_provider = workspace_provider or WorkspaceProvider()

    def load(self) -> SessionState:
        try:
            exists = self.path.exists()
        except OSError:
            return SessionState()
        if not exists:
            return SessionState()
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return SessionState()
        if payload.get("schema_version") != STATE_SCHEMA_VERSION:
            return SessionState()
        return SessionState(
            schema_version=STATE_SCHEMA_VERSION,
            last_repo_path=_coerce_string(payload.get("last_repo_path")),
            recent_repos=_coerce_string_list(payload.get("recent_repos")),
            active_section=_coerce_string(payload.get("active_section")) or "features",
            selected_entity_id=_coerce_string(payload.get("selected_entity_id")),
            filter_text=_coerce_string(payload.get("filter_text")) or "",
            pane_mode=_coerce_string(payload.get("pane_mode")) or "structured",
            table_mode=_coerce_string(payload.get("table_mode")) or "fit",
            selected_columns=_coerce_columns(payload.get("selected_columns")),
        )

    def save(self, session: SessionState) -> None:
        payload = {
            "schema_version": STATE_SCHEMA_VERSION,
            "last_repo_path": session.last_repo_path,
            "recent_repos": session.recent_repos,
            "active_section": session.active_section,
            "selected_entity_id": session.selected_entity_id,
            "filter_text": session.filter_text,
            "pane_mode": session.pane_mode,
            "table_mode": session.table_mode,
            "selected_columns": session.selected_columns,
        }
        try:
            self.path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        except OSError:
            return

    def resolve_startup_path(self, cwd: str | Path, session: SessionState) -> str | None:
        for candidate in (session.last_repo_path, Path(cwd).as_posix()):
            if not candidate:
                continue
            try:
                registry_path = self.workspace_provider.resolve_preferred_registry_path(candidate)
            except FileNotFoundError:
                continue
            return registry_path.parent.parent.as_posix()
        return None


def _coerce_string(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _coerce_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _coerce_columns(value: object) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        return {}
    selected: dict[str, list[str]] = {}
    for section, columns in value.items():
        if not isinstance(section, str) or not isinstance(columns, list):
            continue
        filtered = [column for column in columns if isinstance(column, str) and column]
        if filtered:
            selected[section] = filtered
    return selected
