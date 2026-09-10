from .criterion_evaluator import evaluate_criterion
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

    result_by_id = {item.id: item for item in results}

    for result in results:
        if result.task_id != task.id:
            raise ValueError("result does not belong to task")

    if not evidence:
        return Outcome(
            decision_id=decision.id,
            task_id=task.id,
            status="uncertain",
            summary="no evidence available to evaluate objective",
        )

    for item in evidence:
        result = result_by_id.get(item.result_id)
        if result is None:
            raise ValueError("evidence references unknown result")
        if item.execution_id != result.execution_id:
            raise ValueError("evidence execution does not match result")

    evaluations = [
        (criterion, evaluate_criterion(criterion, evidence))
        for criterion in objective.criteria
    ]

    referenced_result_ids = [item.result_id for item in evidence]
    referenced_evidence_ids = [item.id for item in evidence]

    if any(value is False for _, value in evaluations):
        status = "failure"
    elif all(value is True for _, value in evaluations):
        status = "success"
    else:
        status = "uncertain"

    details = "; ".join(
        f"{criterion.name}: {value if value is not None else 'unknown'}"
        for criterion, value in evaluations
    )

    return Outcome(
        decision_id=decision.id,
        task_id=task.id,
        status=status,
        summary=f"objective evaluation: {details}",
        result_ids=referenced_result_ids,
        evidence_ids=referenced_evidence_ids,
    )
