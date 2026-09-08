from dataclasses import dataclass, field
from typing import List, Optional

from .state import SystemState
from .memory import Memory
from .history import HistoryEvent
from .models import Task
from .goals import Goal


@dataclass
class AgentContext:
    goal_id: Optional[str] = None
    goal: Optional[Goal] = None
    task: Optional[Task] = None
    last_decision_id: Optional[str] = None
    last_result_id: Optional[str] = None

    state: Optional[SystemState] = None
    memories: List[Memory] = field(default_factory=list)
    history: List[HistoryEvent] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)

    @classmethod
    def from_state(cls, state: SystemState) -> "AgentContext":
        return cls(
            goal_id=state.active_goal_id,
            last_decision_id=state.last_decision_id,
            last_result_id=state.last_result_id,
            state=state,
        )
