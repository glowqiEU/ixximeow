from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


CRITERION_KINDS = {"exists", "equals", "contains", "boolean"}


@dataclass
class ObjectiveCriterion:
    """One deterministic condition used to evaluate an objective."""

    claim: str
    kind: str
    expected: Any = None
    id: str = field(default_factory=lambda: str(uuid4()))

    @property
    def name(self) -> str:
        """Backward-compatible display name derived from the canonical claim."""
        return self.claim

    def __post_init__(self) -> None:
        if not self.claim.strip():
            raise ValueError("criterion claim cannot be empty")
        if self.kind not in CRITERION_KINDS:
            raise ValueError(f"invalid criterion kind: {self.kind}")
        if self.kind in {"equals", "contains", "boolean"} and self.expected is None:
            raise ValueError(f"criterion expected is required for {self.kind}")
        if self.kind == "boolean" and not isinstance(self.expected, bool):
            raise ValueError("boolean criterion expected must be a boolean")


@dataclass
class Objective:
    """The explicit, testable definition of what a decision is trying to achieve."""

    decision_id: str
    task_id: str
    description: str
    criteria: list[ObjectiveCriterion]
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not self.decision_id.strip():
            raise ValueError("objective decision_id cannot be empty")
        if not self.task_id.strip():
            raise ValueError("objective task_id cannot be empty")
        if not self.description.strip():
            raise ValueError("objective description cannot be empty")
        if not self.criteria:
            raise ValueError("objective requires at least one criterion")
