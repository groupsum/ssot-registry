from __future__ import annotations

import json
from typing import Any

from textual.widgets import Static


class EntityDetailPane(Static):
    def show_entity(self, entity: dict[str, Any] | None) -> None:
        if entity is None:
            self.update("No entity selected.")
            return
        self.update(json.dumps(entity, indent=2, sort_keys=True))
