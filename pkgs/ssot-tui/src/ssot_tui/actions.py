from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


ActionHandler = Callable[[], None]
ActionEnabled = Callable[[], bool]


@dataclass(frozen=True, slots=True)
class ActionDefinition:
    id: str
    label: str
    description: str
    keybinding: str | None
    scope: str
    handler: ActionHandler
    enabled: ActionEnabled


class ActionRegistry:
    def __init__(self) -> None:
        self._actions: dict[str, ActionDefinition] = {}

    def register(self, action: ActionDefinition) -> None:
        self._actions[action.id] = action

    def get(self, action_id: str) -> ActionDefinition:
        return self._actions[action_id]

    def list_actions(self) -> list[ActionDefinition]:
        return sorted(self._actions.values(), key=lambda action: (action.scope, action.label))

    def enabled_actions(self) -> list[ActionDefinition]:
        return [action for action in self.list_actions() if action.enabled()]
