from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4


EXECUTION_STATUSES = {
    "pending",
    "running",
    "succeeded",
    "failed",
    "uncertain",
}


ALLOWED_TRANSITIONS = {
    "pending": {"running", "failed"},
    "running": {"succeeded", "failed", "uncertain"},
    "succeeded": set(),
    "failed": set(),
    "uncertain": {"running", "failed", "succeeded", "uncertain"},
}


@dataclass
class Execution:
    """A durable logical execution of one concrete action."""

    action_id: str
    task_id: str
    status: str = "pending"
    attempt: int = 0
    idempotency_key: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid4()))
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        if not self.action_id.strip():
            raise ValueError("execution action_id cannot be empty")
        if not self.task_id.strip():
            raise ValueError("execution task_id cannot be empty")
        if self.status not in EXECUTION_STATUSES:
            raise ValueError(f"invalid execution status: {self.status}")
        if self.attempt < 0:
            raise ValueError("execution attempt cannot be negative")

        if self.idempotency_key is None:
            self.idempotency_key = self.action_id
        elif not self.idempotency_key.strip():
            raise ValueError("execution idempotency_key cannot be empty")

    def transition(self, new_status: str) -> None:
        if new_status not in EXECUTION_STATUSES:
            raise ValueError(f"invalid execution status: {new_status}")

        if new_status not in ALLOWED_TRANSITIONS[self.status]:
            raise ValueError(
                f"invalid execution transition: {self.status} -> {new_status}"
            )

        now = datetime.now(timezone.utc).isoformat()

        if new_status == "running":
            self.attempt += 1
            if self.started_at is None:
                self.started_at = now

        if new_status in {"succeeded", "failed"}:
            self.finished_at = now

        self.status = new_status
