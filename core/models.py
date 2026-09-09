from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4
from typing import List, Optional


def new_id() -> str:
    return str(uuid4())


@dataclass
class Decision:
    objective: str
    action: str
    reason: str
    priority: int = 0
    status: str = "proposed"
    goal_id: Optional[str] = None
    id: str = field(default_factory=new_id)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class Plan:
    decision_id: str
    steps: List[str]
    goal_id: Optional[str] = None
    status: str = "proposed"
    id: str = field(default_factory=new_id)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class Task:
    title: str
    status: str = "pending"
    decision_id: Optional[str] = None
    plan_id: Optional[str] = None
    goal_id: Optional[str] = None
    approval_id: Optional[str] = None
    required_level: str = "execute"
    id: str = field(default_factory=new_id)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class Result:
    """Technical result produced by exactly one execution."""

    task_id: str
    action_id: str
    execution_id: str
    success: bool
    summary: str
    id: str = field(default_factory=new_id)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        if not self.task_id.strip():
            raise ValueError("result task_id cannot be empty")
        if not self.action_id.strip():
            raise ValueError("result action_id cannot be empty")
        if not self.execution_id.strip():
            raise ValueError("result execution_id cannot be empty")
        if not isinstance(self.success, bool):
            raise ValueError("result success must be a boolean")
        if not self.summary.strip():
            raise ValueError("result summary must not be empty")
