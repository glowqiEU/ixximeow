from .approval import Approval


ALLOWED_TRANSITIONS = {
    "pending": {"approved", "rejected"},
    "approved": set(),
    "rejected": set(),
}


def transition_approval(approval: Approval, new_status: str) -> Approval:
    allowed = ALLOWED_TRANSITIONS.get(approval.status, set())

    if new_status not in allowed:
        raise ValueError(
            f"invalid approval transition: "
            f"{approval.status} -> {new_status}"
        )

    approval.status = new_status
    return approval
