from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, OptionList
from textual.widgets.option_list import Option

from ssot_tui.actions import ActionDefinition


class CommandPaletteScreen(ModalScreen[str | None]):
    CSS = """
    CommandPaletteScreen {
        align: center middle;
    }

    #command_palette_panel {
        width: 88;
        height: 24;
        border: solid $accent;
        background: $surface;
        padding: 1;
    }
    """

    def __init__(self, actions: list[ActionDefinition]) -> None:
        super().__init__()
        self._actions = actions
        self._filtered = actions

    def compose(self) -> ComposeResult:
        with Vertical(id="command_palette_panel"):
            yield Input(placeholder="Type an action", id="command_palette_query")
            yield OptionList(id="command_palette_options")

    def on_mount(self) -> None:
        self._refresh_options("")
        self.query_one("#command_palette_query", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "command_palette_query":
            self._refresh_options(event.value)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        action_id = getattr(event.option, "id", None)
        if action_id is not None:
            self.dismiss(action_id)

    def key_escape(self) -> None:
        self.dismiss(None)

    def _refresh_options(self, query: str) -> None:
        normalized = query.strip().lower()
        self._filtered = [
            action
            for action in self._actions
            if normalized in action.label.lower() or normalized in action.description.lower()
        ]
        options = [
            Option(
                f"{action.label} [{action.keybinding}]\n{action.description}" if action.keybinding else f"{action.label}\n{action.description}",
                id=action.id,
            )
            for action in self._filtered
        ]
        option_list = self.query_one("#command_palette_options", OptionList)
        if not options:
            option_list.set_options([Option("No matching actions", id="command_palette_empty", disabled=True)])
            return
        option_list.set_options(options)
