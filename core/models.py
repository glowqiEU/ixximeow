from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Decision:
    objective: str
    action: str
    reason: str
    priority: int = 0
    status: str = "proposed"
    id: Optional[str] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class Task:
    title: str
    status: str = "pending"
    decision_id: Optional[str] = None
    id: Optional[str] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class Result:
    task_id: str
    success: bool
    summary: str
    id: Optional[str] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
