from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4


OUTCOME_STATUSES = {"achieved", "not_achieved", "uncertain", "blocked"}
BLOCK_REASONS = {"permission", "execution", "dependency"}


@dataclass
class Outcome:
    """Assessment of whether the original objective was achieved."""

    decision_id: str
    task_id: str
    status: str
    summary: str
    result_ids: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    block_reason: Optional[str] = None
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
        if self.block_reason is not None and self.block_reason not in BLOCK_REASONS:
            raise ValueError(f"invalid outcome block_reason: {self.block_reason}")
        if self.status == "blocked" and self.block_reason is None:
            raise ValueError("blocked outcome requires block_reason")
        if self.status != "blocked" and self.block_reason is not None:
            raise ValueError("block_reason is only valid for blocked outcomes")
