from collections.abc import Callable
from typing import Any

from .action import Action


ActionHandler = Callable[[Action], Any]


class ActionRegistry:
    """Registry mapping explicit action names to deterministic handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, ActionHandler] = {}

    def register(self, name: str, handler: ActionHandler) -> None:
        if not name:
            raise ValueError("action name cannot be empty")
        if name in self._handlers:
            raise ValueError(f"action already registered: {name}")
        self._handlers[name] = handler

    def get(self, name: str) -> ActionHandler:
        try:
            return self._handlers[name]
        except KeyError as exc:
            raise ValueError(f"action not registered: {name}") from exc

    def execute(self, action: Action) -> Any:
        return self.get(action.name)(action)
