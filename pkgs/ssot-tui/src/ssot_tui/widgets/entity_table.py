from __future__ import annotations

from typing import Any

from ssot_contracts.generated.python.tui_metadata import ENTITY_VIEW_SECTIONS
from textual.widgets import DataTable


class EntityTable(DataTable):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.cursor_type = "row"
        self.zebra_stripes = True
        self._rows: list[dict[str, Any]] = []

    def load_rows(self, section: str, rows: list[dict[str, Any]]) -> None:
        self._rows = list(rows)
        self.clear(columns=True)
        columns = ENTITY_VIEW_SECTIONS.get(section, ("id", "title", "status"))
        self.add_columns(*columns)
        for row in rows:
            self.add_row(*(str(row.get(column, "")) for column in columns), key=str(row.get("id", "")))

    def entity_for_row_index(self, row_index: int) -> dict[str, Any] | None:
        if row_index < 0 or row_index >= len(self._rows):
            return None
        return self._rows[row_index]

    def row_index_for_entity_id(self, entity_id: str) -> int | None:
        for index, row in enumerate(self._rows):
            if row.get("id") == entity_id:
                return index
        return None
