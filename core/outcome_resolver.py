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
    """Resolve objective status conservatively from explicit evidence."""
    if objective.decision_id != decision.id:
        raise ValueError("objective does not belong to decision")
    if objective.task_id != task.id:
        raise ValueError("objective does not belong to task")

    result_by_id = {item.id: item for item in results}
    valid_evidence = [
        item
        for item in evidence
        if item.result_id in result_by_id
        and item.execution_id == result_by_id[item.result_id].execution_id
    ]

    if not valid_evidence:
        return Outcome(
            decision_id=decision.id,
            task_id=task.id,
            status="uncertain",
            summary="no valid evidence available to evaluate objective",
        )

    referenced_result_ids = list(dict.fromkeys(item.result_id for item in valid_evidence))
    referenced_evidence_ids = [item.id for item in valid_evidence]
    criterion_names = ", ".join(criterion.name for criterion in objective.criteria)

    # v1 intentionally refuses to infer semantic truth from free-form evidence.
    # Explicit criterion evaluation is the next contract layer.
    return Outcome(
        decision_id=decision.id,
        task_id=task.id,
        status="uncertain",
        summary=f"objective criteria require explicit evaluation: {criterion_names}",
        result_ids=referenced_result_ids,
        evidence_ids=referenced_evidence_ids,
    )
