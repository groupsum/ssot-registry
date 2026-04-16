from __future__ import annotations

from textual.widgets import Tree

from ssot_tui.services import ENTITY_SECTIONS


class SectionNavigation(Tree[str]):
    def __init__(self) -> None:
        super().__init__("Registry")
        self.show_root = True

    def on_mount(self) -> None:
        root = self.root
        root.expand()
        for section, label in ENTITY_SECTIONS:
            root.add_leaf(label, data=section)
