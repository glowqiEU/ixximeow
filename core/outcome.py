from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4


OUTCOME_STATUSES = {"success", "failure", "uncertain"}


@dataclass
class Outcome:
    """Conservative assessment of whether a task objective was achieved."""

    task_id: str
    success: Optional[bool] = None
    summary: str = ""
    decision_id: Optional[str] = None
    status: Optional[str] = None
    result_ids: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        if not self.task_id.strip():
            raise ValueError("outcome task_id cannot be empty")
        if self.decision_id is not None and not self.decision_id.strip():
            raise ValueError("outcome decision_id cannot be empty")
        if not self.summary.strip():
            raise ValueError("outcome summary cannot be empty")

        if self.status is None:
            if self.success is True:
                self.status = "success"
            elif self.success is False:
                self.status = "failure"
            else:
                self.status = "uncertain"
        elif self.status not in OUTCOME_STATUSES:
            raise ValueError(f"invalid outcome status: {self.status}")

        if self.success is not None:
            expected_status = "success" if self.success else "failure"
            if self.status != expected_status:
                raise ValueError("outcome success does not match status")
