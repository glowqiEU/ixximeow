from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from .permissions import AutonomyLevel


@dataclass
class Action:
    """A concrete operation selected for execution."""

    task_id: str
    name: str
    input: dict[str, Any] = field(default_factory=dict)
    permission_level: str = "execute"
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not self.task_id.strip():
            raise ValueError("action task_id cannot be empty")
        if not self.name.strip():
            raise ValueError("action name cannot be empty")

        try:
            AutonomyLevel[self.permission_level.upper()]
        except KeyError as exc:
            raise ValueError(
                f"invalid action permission level: {self.permission_level}"
            ) from exc
