from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header

from .screens import BrowserScreen


class SsotTuiApp(App[None]):
    TITLE = "SSOT TUI"
    SUB_TITLE = "Registry browser"
    BINDINGS = [
        Binding(
            "ctrl+c",
            "hard_exit",
            "Hard exit",
            show=False,
            priority=True,
            system=True,
        ),
    ]
    CSS = """
    Screen {
        layout: vertical;
    }

    #startup_panel {
        height: auto;
        border: solid $accent 20%;
        padding: 1;
        margin-bottom: 1;
    }

    #repo_path, #filter_input {
        margin-bottom: 1;
    }

    #browser {
        height: 1fr;
    }

    SectionNavigation {
        width: 32;
        border: solid $accent;
    }

    EntityTable {
        width: 1fr;
        border: solid $accent 40%;
    }

    EntityDetailPane {
        width: 42;
        border: solid $accent 20%;
        overflow: auto;
    }

    #summary_row {
        height: auto;
        padding: 0 1;
    }

    #summary_status {
        width: 1fr;
        color: $text-muted;
    }

    #workspace_status {
        width: 1fr;
        color: $text;
        padding: 0 1;
    }

    #validation_status {
        width: auto;
        color: $warning;
    }

    #status_center {
        height: 7;
        border: solid $accent 20%;
        padding: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()

    def on_mount(self) -> None:
        self.push_screen(BrowserScreen())

    def action_hard_exit(self) -> None:
        self.exit(return_code=130)

    def action_help_quit(self) -> None:
        self.action_hard_exit()
