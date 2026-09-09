from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from .permissions import AutonomyLevel


APPROVAL_STATUSES = {"pending", "approved", "rejected", "cancelled"}


@dataclass
class Approval:
    """A human authorization bound to one concrete action."""

    action_id: str
    task_id: str
    required_level: str
    reason: str
    status: str = "pending"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        if not self.action_id.strip():
            raise ValueError("approval action_id cannot be empty")
        if not self.task_id.strip():
            raise ValueError("approval task_id cannot be empty")
        if not self.reason.strip():
            raise ValueError("approval reason cannot be empty")
        if self.status not in APPROVAL_STATUSES:
            raise ValueError(f"invalid approval status: {self.status}")

        try:
            AutonomyLevel[self.required_level.upper()]
        except KeyError as exc:
            raise ValueError(
                f"invalid approval required level: {self.required_level}"
            ) from exc
