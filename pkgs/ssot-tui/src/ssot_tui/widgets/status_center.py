from __future__ import annotations

from textual.widgets import Static


class StatusCenter(Static):
    def show_messages(self, messages: list[str]) -> None:
        if not messages:
            self.update("No status yet.")
            return
        self.update("\n".join(f"- {message}" for message in messages[-6:]))
