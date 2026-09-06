from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class SystemState:
    active_goal_id: Optional[str] = None
    active_task: Optional[str] = None
    last_decision_id: Optional[str] = None
    last_result_id: Optional[str] = None
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
