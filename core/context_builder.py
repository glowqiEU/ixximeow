from typing import Optional

from .context import AgentContext
from .state_store import load_state
from .memory_store import load_memories
from .memory_retriever import retrieve_memories
from .history_store import load_events
from .task_store import load_tasks
from .goal_store import get_goal


def build_context(
    state=None,
    memories=None,
    history=None,
    tasks=None,
    goal=None,
    query: Optional[str] = None,
) -> AgentContext:
    current_state = state if state is not None else load_state()
    all_memories = memories if memories is not None else load_memories()
    all_tasks = tasks if tasks is not None else load_tasks()

    resolved_goal = goal
    if resolved_goal is None and current_state.active_goal_id is not None:
        resolved_goal = get_goal(current_state.active_goal_id)

    active_task = None
    if current_state.active_task is not None:
        active_task = next(
            (task for task in all_tasks if task.id == current_state.active_task),
            None,
        )
        if active_task is None:
            raise ValueError(
                f"active task not found: {current_state.active_task}"
            )

        if (
            current_state.active_goal_id is not None
            and active_task.goal_id != current_state.active_goal_id
        ):
            raise ValueError("active task does not belong to active goal")

    relevant_memories = (
        retrieve_memories(query, all_memories)
        if query
        else all_memories
    )

    return AgentContext(
        goal_id=current_state.active_goal_id,
        goal=resolved_goal,
        task=active_task,
        last_decision_id=current_state.last_decision_id,
        last_result_id=current_state.last_result_id,
        state=current_state,
        memories=relevant_memories,
        history=history if history is not None else load_events(),
        tasks=all_tasks,
    )
