from .models import Decision, Plan


def build_plan(decision: Decision) -> Plan:
    """Translate a selected decision into executable planning steps.

    The first implementation is intentionally one-step: planning establishes
    the contract without pretending that decomposition is more sophisticated
    than it currently is.
    """
    if not decision.action.strip():
        raise ValueError("decision action cannot be empty")

    return Plan(
        decision_id=decision.id,
        goal_id=decision.goal_id,
        steps=[decision.action],
    )
