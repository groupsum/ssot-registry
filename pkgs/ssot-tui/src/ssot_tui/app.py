from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from .screens import BrowserScreen


class SsotTuiApp(App[None]):
    TITLE = "SSOT TUI"
    SUB_TITLE = "Registry browser"
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
