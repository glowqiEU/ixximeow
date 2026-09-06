from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4


@dataclass
class Goal:
    title: str
    description: str
    priority: int = 0
    status: str = "active"
    metrics: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    id: Optional[str] = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
