from typing import Optional

from .context import AgentContext


def build_memory_query(context: AgentContext) -> Optional[str]:
    if context.task:
        return context.task.title if hasattr(context.task, "title") else context.task

    return None
