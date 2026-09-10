from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ActionResponse:
    """Deterministic output returned by an action handler before Result creation."""

    success: bool
    summary: str
    output: Any = None

    def __post_init__(self) -> None:
        if not isinstance(self.success, bool):
            raise ValueError("action response success must be a boolean")
        if not self.summary.strip():
            raise ValueError("action response summary cannot be empty")
