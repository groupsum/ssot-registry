from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Markdown, OptionList
from textual.widgets.option_list import Option

from ssot_tui.presentations import EntityDetailViewModel, render_entity_markdown, render_raw_entity_markdown


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
        self._raw_json = ""
        self._current_markdown = placeholder
        self._pending_markdown: str | None = None
        self._markdown_update_running = False

    def compose(self) -> ComposeResult:
        yield Markdown(self._placeholder, id="entity_detail_body", open_links=False)
        yield OptionList(id="entity_detail_resources")

    def show_entity(
        self,
        entity: dict[str, Any] | None,
        *,
        workspace_root: str | Path | None = None,
        entity_index: dict[str, tuple[str, dict[str, Any]]] | None = None,
    ) -> None:
        if entity is None:
            self._update_body(self._placeholder)
            self._raw_json = ""
            self._set_targets([])
            return
        self._raw_json = json.dumps(entity, indent=2, sort_keys=True)
        self._update_body(render_raw_entity_markdown(self._raw_json))
        self._set_targets(self._build_targets(entity, workspace_root=workspace_root, entity_index=entity_index or {}))

    def show_resource_text(self, title: str, text: str) -> None:
        self._update_body(f"# {title}\n\n{text}")
        self._set_targets([])

    def show_view_model(self, view_model: EntityDetailViewModel, *, raw_mode: bool) -> None:
        self._raw_json = view_model.raw_json
        self._update_body(render_raw_entity_markdown(view_model.raw_json) if raw_mode else render_entity_markdown(view_model))
        self._set_targets(
            [
                TraversalTarget(
                    kind=resource.kind,
                    value=resource.value,
                    label=resource.label,
                    field_path=resource.field_path,
                    section=resource.section,
                    absolute_path=resource.absolute_path,
                )
                for resource in view_model.resources
            ]
        )

    def toggle_raw_mode(self, *, raw_mode: bool, view_model: EntityDetailViewModel | None) -> None:
        if view_model is None:
            return
        self.show_view_model(view_model, raw_mode=raw_mode)

    def _update_body(self, markdown: str) -> None:
        self._current_markdown = markdown
        self._pending_markdown = markdown
        if not self._markdown_update_running:
            self._markdown_update_running = True
            self.run_worker(
                self._flush_markdown_updates(),
                group="entity_detail_markdown",
                exclusive=True,
                exit_on_error=False,
            )

    async def _flush_markdown_updates(self) -> None:
        try:
            body = self.query_one("#entity_detail_body", Markdown)
            while self._pending_markdown is not None:
                markdown = self._pending_markdown
                self._pending_markdown = None
                await body.update(markdown)
        finally:
            self._markdown_update_running = False
            if self._pending_markdown is not None and self.is_mounted:
                self._update_body(self._pending_markdown)

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
            if field_path == "id" and value == entity.get("id"):
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
