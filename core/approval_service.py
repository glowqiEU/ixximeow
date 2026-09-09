from typing import Optional

from .action import Action
from .approval import Approval
from .permissions import AutonomyLevel, requires_approval


def create_approval_if_needed(
    action: Action,
    current_level: AutonomyLevel,
    reason: str,
) -> Optional[Approval]:
    required_level = AutonomyLevel[action.permission_level.upper()]

    if not requires_approval(current_level, required_level):
        return None

    return Approval(
        action_id=action.id,
        task_id=action.task_id,
        required_level=required_level.name.lower(),
        reason=reason,
    )
