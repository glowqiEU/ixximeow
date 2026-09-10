from collections.abc import Callable

from .action import Action
from .action_response import ActionResponse


ActionHandler = Callable[[Action], ActionResponse]


class ActionDispatchError(ValueError):
    """Raised when an action cannot be dispatched to a registered handler."""


class ActionContractError(TypeError):
    """Raised when an action handler violates the response contract."""


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
            raise ActionDispatchError(f"action not registered: {name}") from exc

    def execute(self, action: Action) -> ActionResponse:
        response = self.get(action.name)(action)
        if not isinstance(response, ActionResponse):
            raise ActionContractError("action handler must return ActionResponse")
        return response
