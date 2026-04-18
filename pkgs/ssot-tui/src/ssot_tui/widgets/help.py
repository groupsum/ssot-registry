from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static

from ssot_tui.actions import ActionDefinition


class HelpScreen(ModalScreen[None]):
    CSS = """
    HelpScreen {
        align: center middle;
    }

    #help_panel {
        width: 96;
        height: 28;
        border: solid $accent;
        background: $surface;
        padding: 1 2;
    }
    """

    def __init__(self, actions: list[ActionDefinition]) -> None:
        super().__init__()
        self._actions = actions

    def compose(self) -> ComposeResult:
        body = ["Keyboard and actions", ""]
        for action in self._actions:
            shortcut = action.keybinding or "-"
            body.append(f"{shortcut:>10}  {action.label}  {action.description}")
        with Vertical(id="help_panel"):
            yield Static("\n".join(body), id="help_body")

    def key_escape(self) -> None:
        self.dismiss(None)
