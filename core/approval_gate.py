from typing import Optional

from .action import Action
from .approval import Approval
from .approval_service import create_approval_if_needed
from .agent_config import CURRENT_AUTONOMY_LEVEL


def check_approval(action: Action) -> Optional[Approval]:
    """Return a human approval request for this concrete action when needed."""
    return create_approval_if_needed(
        action=action,
        current_level=CURRENT_AUTONOMY_LEVEL,
        reason=f"action requires {action.permission_level} autonomy level",
    )
