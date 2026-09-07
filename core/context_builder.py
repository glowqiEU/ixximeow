from .context import AgentContext
from .state_store import load_state
from .memory_store import load_memories
from .history_store import load_events
from .task_store import load_tasks


def build_context(
    state=None,
    memories=None,
    history=None,
    tasks=None,
) -> AgentContext:
    return AgentContext(
        goal_id=state.active_goal_id if state is not None else load_state().active_goal_id,
        task=state.active_task if state is not None else load_state().active_task,
        last_decision_id=(
            state.last_decision_id if state is not None else load_state().last_decision_id
        ),
        last_result_id=(
            state.last_result_id if state is not None else load_state().last_result_id
        ),
        state=state if state is not None else load_state(),
        memories=memories if memories is not None else load_memories(),
        history=history if history is not None else load_events(),
        tasks=tasks if tasks is not None else load_tasks(),
    )
