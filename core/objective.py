from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


CRITERION_KINDS = {"exists", "equals", "contains", "boolean"}


@dataclass
class ObjectiveCriterion:
    """One explicit condition that can be evaluated against evidence."""

    name: str
    kind: str
    expected: Any = None
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("objective criterion name cannot be empty")
        if self.kind not in CRITERION_KINDS:
            raise ValueError(f"invalid objective criterion kind: {self.kind}")

        if self.kind in {"equals", "contains", "boolean"} and self.expected is None:
            raise ValueError("objective criterion expected value is required")


@dataclass
class Objective:
    """The success contract that an outcome must evaluate."""

    decision_id: str
    task_id: str
    description: str
    criteria: list[ObjectiveCriterion] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not self.decision_id.strip():
            raise ValueError("objective decision_id cannot be empty")
        if not self.task_id.strip():
            raise ValueError("objective task_id cannot be empty")
        if not self.description.strip():
            raise ValueError("objective description cannot be empty")
        if not self.criteria:
            raise ValueError("objective must contain at least one criterion")
