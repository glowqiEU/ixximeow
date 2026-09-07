from typing import Optional

from .context import AgentContext
from .state_store import load_state
from .memory_store import load_memories
from .memory_retriever import retrieve_memories
from .history_store import load_events
from .task_store import load_tasks


def build_context(
    state=None,
    memories=None,
    history=None,
    tasks=None,
    query: Optional[str] = None,
) -> AgentContext:
    current_state = state if state is not None else load_state()
    all_memories = memories if memories is not None else load_memories()

    relevant_memories = (
        retrieve_memories(query, all_memories)
        if query
        else all_memories
    )

    return AgentContext(
        goal_id=current_state.active_goal_id,
        task=current_state.active_task,
        last_decision_id=current_state.last_decision_id,
        last_result_id=current_state.last_result_id,
        state=current_state,
        memories=relevant_memories,
        history=history if history is not None else load_events(),
        tasks=tasks if tasks is not None else load_tasks(),
    )
