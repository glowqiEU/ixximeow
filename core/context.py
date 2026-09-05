from dataclasses import dataclass
from typing import Optional

from .state import SystemState


@dataclass
class AgentContext:
    goal: Optional[str]
    task: Optional[str]
    last_decision_id: Optional[str]
    last_result_id: Optional[str]

    @classmethod
    def from_state(cls, state: SystemState) -> "AgentContext":
        return cls(
            goal=state.active_goal,
            task=state.active_task,
            last_decision_id=state.last_decision_id,
            last_result_id=state.last_result_id,
        )
