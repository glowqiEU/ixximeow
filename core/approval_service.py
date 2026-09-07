from typing import Optional

from .approval import Approval
from .permissions import AutonomyLevel, requires_approval


def create_approval_if_needed(
    task_id: str,
    current_level: AutonomyLevel,
    required_level: AutonomyLevel,
    reason: str,
) -> Optional[Approval]:
    if not requires_approval(current_level, required_level):
        return None

    return Approval(
        task_id=task_id,
        required_level=required_level.name.lower(),
        reason=reason,
    )
