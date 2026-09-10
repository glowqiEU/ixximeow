from dataclasses import dataclass
from typing import Optional


RECONCILIATION_STATUSES = {"already_succeeded", "not_executed", "unknown"}


@dataclass(frozen=True)
class Reconciliation:
    """Structured external-state result for an uncertain execution."""

    status: str
    summary: str
    source: Optional[str] = None

    def __post_init__(self) -> None:
        if self.status not in RECONCILIATION_STATUSES:
            raise ValueError(f"invalid reconciliation status: {self.status}")
        if not self.summary.strip():
            raise ValueError("reconciliation summary must not be empty")
        if self.source is not None and not self.source.strip():
            raise ValueError("reconciliation source must not be empty")
