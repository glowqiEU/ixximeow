from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class HistoryEvent:
    event_type: str
    summary: str
    decision_id: Optional[str] = None
    task_id: Optional[str] = None
    result_id: Optional[str] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
