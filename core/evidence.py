from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class Evidence:
    """Recorded evidence linking an observation to an execution result."""

    result_id: str
    execution_id: str
    kind: str
    content: str
    verified: bool = False
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        if not self.result_id.strip():
            raise ValueError("evidence result_id cannot be empty")
        if not self.execution_id.strip():
            raise ValueError("evidence execution_id cannot be empty")
        if not self.kind.strip():
            raise ValueError("evidence kind cannot be empty")
        if not self.content.strip():
            raise ValueError("evidence content cannot be empty")
