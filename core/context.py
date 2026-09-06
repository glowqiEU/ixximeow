from dataclasses import dataclass
from typing import Optional

from .state import SystemState


@dataclass
class AgentContext:
    goal_id: Optional[str] = None
    task: Optional[str] = None
    last_decision_id: Optional[str] = None
    last_result_id: Optional[str] = None

    @classmethod
    def from_state(cls, state: SystemState) -> "AgentContext":
        return cls(
            goal_id=state.active_goal_id,
            task=state.active_task,
            last_decision_id=state.last_decision_id,
            last_result_id=state.last_result_id,
        )
