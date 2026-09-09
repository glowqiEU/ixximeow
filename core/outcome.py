from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4


OUTCOME_STATUSES = {"achieved", "not_achieved", "uncertain", "blocked"}


@dataclass
class Outcome:
    """Assessment of whether the original objective was achieved."""

    decision_id: str
    task_id: str
    status: str
    summary: str
    result_ids: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        if not self.decision_id.strip():
            raise ValueError("outcome decision_id cannot be empty")
        if not self.task_id.strip():
            raise ValueError("outcome task_id cannot be empty")
        if self.status not in OUTCOME_STATUSES:
            raise ValueError(f"invalid outcome status: {self.status}")
        if not self.summary.strip():
            raise ValueError("outcome summary must not be empty")
        if not all(item.strip() for item in self.result_ids):
            raise ValueError("outcome result_ids cannot contain empty ids")
        if not all(item.strip() for item in self.evidence_ids):
            raise ValueError("outcome evidence_ids cannot contain empty ids")
