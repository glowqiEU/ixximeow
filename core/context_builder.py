from .context import AgentContext
from .history_store import load_events
from .state import SystemState
from .state_store import load_state


def build_context(history_limit: int = 10) -> tuple[AgentContext, list]:
    state: SystemState = load_state()
    context = AgentContext.from_state(state)
    recent_history = load_events(limit=history_limit)

    return context, recent_history
