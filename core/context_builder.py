from .context import AgentContext
from .history_store import load_events
from .state import SystemState


def build_context(
    state: SystemState,
    history_limit: int = 10,
) -> tuple[AgentContext, list]:
    context = AgentContext.from_state(state)
    recent_history = load_events(limit=history_limit)

    return context, recent_history
