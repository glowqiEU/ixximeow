from dataclasses import dataclass
from typing import Any, Optional


EXECUTION_DISPOSITION_STATUSES = {"succeeded", "failed", "uncertain"}


@dataclass(frozen=True)
class ExecutionDisposition:
    """Explicit technical disposition returned by an action boundary."""

    status: str
    summary: str
    output: Optional[Any] = None

    def __post_init__(self) -> None:
        if self.status not in EXECUTION_DISPOSITION_STATUSES:
            raise ValueError(f"invalid execution disposition: {self.status}")
        if not self.summary.strip():
            raise ValueError("execution disposition summary cannot be empty")
