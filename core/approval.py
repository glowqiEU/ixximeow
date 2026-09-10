from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from .permissions import AutonomyLevel


APPROVAL_STATUSES = {"pending", "approved", "rejected", "cancelled"}

ALLOWED_TRANSITIONS = {
    "pending": {"approved", "rejected", "cancelled"},
    "approved": set(),
    "rejected": set(),
    "cancelled": set(),
}


@dataclass
class Approval:
    """A human authorization bound to one exact action definition."""

    action_id: str
    task_id: str
    required_level: str
    reason: str
    action_fingerprint: str = ""
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

        if self.action_fingerprint and len(self.action_fingerprint) != 64:
            raise ValueError("approval action_fingerprint must be a sha256 hex digest")

    def transition(self, new_status: str) -> "Approval":
        if new_status not in APPROVAL_STATUSES:
            raise ValueError(f"invalid approval status: {new_status}")

        allowed = ALLOWED_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValueError(
                f"invalid approval transition: {self.status} -> {new_status}"
            )

        self.status = new_status
        return self
