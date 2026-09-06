from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4
from typing import Optional


def new_id() -> str:
    return str(uuid4())


@dataclass
class Decision:
    objective: str
    action: str
    reason: str
    priority: int = 0
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
    id: str = field(default_factory=new_id)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class Result:
    task_id: str
    success: bool
    summary: str
    id: str = field(default_factory=new_id)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
