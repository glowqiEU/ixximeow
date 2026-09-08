from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass
class Action:
    """A concrete operation selected for execution."""

    task_id: str
    name: str
    input: dict[str, Any] = field(default_factory=dict)
    permission_level: str = "execute"
    id: str = field(default_factory=lambda: str(uuid4()))
