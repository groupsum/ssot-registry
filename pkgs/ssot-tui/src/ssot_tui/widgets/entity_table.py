from __future__ import annotations

from typing import Any

from textual.widgets import DataTable

from ssot_tui.presentations import EntityRowViewModel


class EntityTable(DataTable):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.cursor_type = "row"
        self.zebra_stripes = True
        self._rows: list[EntityRowViewModel] = []
        self._columns: list[str] = []
        self._content_signature: tuple[tuple[str, ...], tuple[tuple[str, tuple[tuple[str, str], ...]], ...]] | None = None

    def load_rows(self, columns: list[str], rows: list[EntityRowViewModel]) -> bool:
        signature = (
            tuple(columns),
            tuple((row.entity_id, tuple((column, row.cells.get(column, "")) for column in columns)) for row in rows),
        )
        self._rows = list(rows)
        if self._content_signature == signature:
            return False
        self._content_signature = signature
        self._columns = list(columns)
        self._rows = list(rows)
        self.clear(columns=True)
        widths = self._column_widths(columns, rows)
        for column in columns:
            self.add_column(column, width=widths[column], key=column)
        for row in rows:
            self.add_row(*(row.cells.get(column, "") for column in columns), key=row.entity_id)
        return True

    def entity_for_row_index(self, row_index: int) -> dict[str, Any] | None:
        if row_index < 0 or row_index >= len(self._rows):
            return None
        return self._rows[row_index].raw_entity

    def row_index_for_entity_id(self, entity_id: str) -> int | None:
        for index, row in enumerate(self._rows):
            if row.entity_id == entity_id:
                return index
        return None

    def _column_widths(self, columns: list[str], rows: list[EntityRowViewModel]) -> dict[str, int]:
        widths: dict[str, int] = {}
        for column in columns:
            max_cell_width = max((len(row.cells.get(column, "")) for row in rows), default=0)
            max_width = 72 if column == "path" else 36
            widths[column] = min(max(len(column), max_cell_width, 8), max_width)
        return widths
