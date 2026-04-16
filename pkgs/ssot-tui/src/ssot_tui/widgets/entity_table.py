from __future__ import annotations

from typing import Any

from ssot_contracts.generated.python.tui_metadata import ENTITY_VIEW_SECTIONS
from textual.widgets import DataTable


class EntityTable(DataTable):
    def load_rows(self, section: str, rows: list[dict[str, Any]]) -> None:
        self.clear(columns=True)
        columns = ENTITY_VIEW_SECTIONS.get(section, ("id", "title", "status"))
        self.add_columns(*columns)
        for row in rows:
            self.add_row(*(str(row.get(column, "")) for column in columns))
