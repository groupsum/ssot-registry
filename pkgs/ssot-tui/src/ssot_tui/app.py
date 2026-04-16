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

    #browser {
        height: 1fr;
    }

    SectionNavigation {
        width: 28;
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

    #status {
        padding: 0 1;
        color: $text-muted;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()

    def on_mount(self) -> None:
        self.push_screen(BrowserScreen())
