from typing import Optional

from .approval import Approval
from .approval_service import create_approval_if_needed
from . import agent_config
from .models import Task
from .permissions import AutonomyLevel


def check_approval(task: Task) -> Optional[Approval]:
    required_level = AutonomyLevel[task.required_level.upper()]

    return create_approval_if_needed(
        task_id=task.id,
        current_level=agent_config.CURRENT_AUTONOMY_LEVEL,
        required_level=required_level,
        reason=f"task requires {task.required_level} autonomy level",
    )
