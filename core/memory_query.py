from typing import Optional

from .context import AgentContext


def build_memory_query(context: AgentContext) -> Optional[str]:
    if context.task:
        if isinstance(context.task, str):
            return context.task
        return context.task.title

    return None
