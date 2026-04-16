from __future__ import annotations

from typing import Any

from textual.widgets import DataTable


class EntityTable(DataTable):
    def load_rows(self, rows: list[dict[str, Any]]) -> None:
        self.clear(columns=True)
        self.add_columns("id", "title", "status")
        for row in rows:
            self.add_row(
                str(row.get("id", "")),
                str(row.get("title", "")),
                str(row.get("status", row.get("kind", ""))),
            )
