from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import OptionList, Static
from textual.widgets.option_list import Option


@dataclass(frozen=True, slots=True)
class TraversalTarget:
    kind: str
    value: str
    label: str
    field_path: str
    section: str | None = None
    absolute_path: str | None = None


class EntityDetailPane(Vertical):
    class ResourceSelected(Message):
        def __init__(self, pane: "EntityDetailPane", target: TraversalTarget) -> None:
            super().__init__()
            self.pane = pane
            self.target = target

    def __init__(self, placeholder: str = "No entity selected.", *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._placeholder = placeholder
        self._targets: dict[str, TraversalTarget] = {}

    def compose(self) -> ComposeResult:
        yield Static(self._placeholder, id="entity_detail_body")
        yield OptionList(id="entity_detail_resources")

    def show_entity(
        self,
        entity: dict[str, Any] | None,
        *,
        workspace_root: str | Path | None = None,
        entity_index: dict[str, tuple[str, dict[str, Any]]] | None = None,
    ) -> None:
        body = self.query_one("#entity_detail_body", Static)
        if entity is None:
            body.update(self._placeholder)
            self._set_targets([])
            return
        body.update(json.dumps(entity, indent=2, sort_keys=True))
        self._set_targets(self._build_targets(entity, workspace_root=workspace_root, entity_index=entity_index or {}))

    def show_resource_text(self, title: str, text: str) -> None:
        self.query_one("#entity_detail_body", Static).update(f"{title}\n\n{text}")
        self._set_targets([])

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option = event.option
        option_id = getattr(option, "id", None)
        if option_id is None:
            return
        target = self._targets.get(option_id)
        if target is None:
            return
        self.post_message(self.ResourceSelected(self, target))

    def _set_targets(self, targets: list[TraversalTarget]) -> None:
        option_list = self.query_one("#entity_detail_resources", OptionList)
        self._targets = {f"resource-{index}": target for index, target in enumerate(targets)}
        if not self._targets:
            option_list.clear_options()
            option_list.add_option(Option("No linked resources", id="placeholder", disabled=True))
            return
        option_list.set_options(
            [
                Option(self._format_target_prompt(target), id=option_id)
                for option_id, target in self._targets.items()
            ]
        )

    def _format_target_prompt(self, target: TraversalTarget) -> str:
        prefix = "Entity" if target.kind == "entity" else "File"
        return f"{prefix}: {target.field_path} -> {target.label}"

    def _build_targets(
        self,
        entity: dict[str, Any],
        *,
        workspace_root: str | Path | None,
        entity_index: dict[str, tuple[str, dict[str, Any]]],
    ) -> list[TraversalTarget]:
        root = Path(workspace_root) if workspace_root is not None else None
        targets: list[TraversalTarget] = []
        seen: set[tuple[str, str]] = set()

        def walk(value: Any, field_path: str) -> None:
            if isinstance(value, dict):
                for key, nested in value.items():
                    nested_path = f"{field_path}.{key}" if field_path else key
                    walk(nested, nested_path)
                return
            if isinstance(value, list):
                for index, nested in enumerate(value):
                    nested_path = f"{field_path}[{index}]"
                    walk(nested, nested_path)
                return
            if not isinstance(value, str):
                return

            if value in entity_index:
                section, row = entity_index[value]
                key = ("entity", value)
                if key not in seen:
                    seen.add(key)
                    targets.append(
                        TraversalTarget(
                            kind="entity",
                            value=value,
                            label=str(row.get("title") or row.get("version") or value),
                            field_path=field_path,
                            section=section,
                        )
                    )
                return

            if root is not None and field_path.split(".")[-1] == "path":
                target_path = root / value
                if target_path.exists():
                    key = ("file", target_path.as_posix())
                    if key not in seen:
                        seen.add(key)
                        targets.append(
                            TraversalTarget(
                                kind="file",
                                value=value,
                                label=value,
                                field_path=field_path,
                                absolute_path=target_path.as_posix(),
                            )
                        )

        walk(entity, "")
        return targets
