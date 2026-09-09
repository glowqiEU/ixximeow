from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4


EVIDENCE_KINDS = {"execution_output", "external_observation", "verification"}


@dataclass
class Evidence:
    """A traceable, optionally verified fact that can support an objective."""

    result_id: str
    execution_id: str
    kind: str
    claim: str
    value: Any = None
    content: str = ""
    source: Optional[str] = None
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
        if self.kind not in EVIDENCE_KINDS:
            raise ValueError(f"invalid evidence kind: {self.kind}")
        if not self.claim.strip():
            raise ValueError("evidence claim cannot be empty")
        if not self.content.strip():
            raise ValueError("evidence content must not be empty")
        if self.source is not None and not self.source.strip():
            raise ValueError("evidence source cannot be empty when supplied")
        if not isinstance(self.verified, bool):
            raise ValueError("evidence verified must be a boolean")
