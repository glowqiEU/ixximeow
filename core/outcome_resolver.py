from .evidence import Evidence
from .models import Decision, Result, Task
from .objective import Objective
from .outcome import Outcome


def resolve_outcome(
    decision: Decision,
    task: Task,
    objective: Objective,
    results: list[Result],
    evidence: list[Evidence],
) -> Outcome:
    """Resolve objective status from explicit criteria and recorded evidence."""
    if objective.decision_id != decision.id:
        raise ValueError("objective does not belong to decision")
    if objective.task_id != task.id:
        raise ValueError("objective does not belong to task")

    evidence_by_id = {item.id: item for item in evidence}
    result_by_id = {item.id: item for item in results}

    if not evidence:
        return Outcome(
            decision_id=decision.id,
            task_id=task.id,
            status="uncertain",
            summary="no evidence available to evaluate objective",
        )

    missing_criteria = [criterion.name for criterion in objective.criteria]

    # v1 deliberately does not guess semantic matches. Criteria evaluation
    # becomes explicit in the next resolver layer; until then, evidence can
    # establish provenance but not silently prove an objective.
    referenced_result_ids = [item.result_id for item in evidence if item.result_id in result_by_id]
    referenced_evidence_ids = [item.id for item in evidence if item.id in evidence_by_id]

    return Outcome(
        decision_id=decision.id,
        task_id=task.id,
        status="uncertain",
        summary=(
            "objective criteria require explicit evaluation: "
            + ", ".join(missing_criteria)
        ),
        result_ids=referenced_result_ids,
        evidence_ids=referenced_evidence_ids,
    )
