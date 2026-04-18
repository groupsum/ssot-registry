from __future__ import annotations

from typing import Any

from textual.widgets import Tree

class SectionNavigation(Tree[str]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__("Registry", *args, **kwargs)
        self.show_root = True
        self._leaf_ids: dict[str, object] = {}

    def load_sections(
        self,
        sections: tuple[tuple[str, str], ...],
        *,
        counts: dict[str, int] | None = None,
        failures: dict[str, int] | None = None,
    ) -> None:
        root = self.root
        root.remove_children()
        root.expand()
        counts = counts or {}
        failures = failures or {}
        for section, label in sections:
            count = counts.get(section, 0)
            failure_count = failures.get(section, 0)
            failure_suffix = f" !{failure_count}" if failure_count else ""
            node = root.add_leaf(f"{label} ({count}){failure_suffix}", data=section)
            self._leaf_ids[section] = node.id
