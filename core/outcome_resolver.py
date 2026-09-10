from .criterion_evaluator import evaluate_criteria
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
    """Resolve objective status from explicit, provenance-safe criteria."""
    if objective.decision_id != decision.id:
        raise ValueError("objective does not belong to decision")
    if objective.task_id != task.id:
        raise ValueError("objective does not belong to task")

    result_by_id = {
        item.id: item
        for item in results
        if item.task_id == task.id
    }
    valid_evidence = [
        item
        for item in evidence
        if item.result_id in result_by_id
        and item.execution_id == result_by_id[item.result_id].execution_id
    ]

    evaluations = evaluate_criteria(objective.criteria, valid_evidence)

    statuses = [evaluation.status for evaluation in evaluations]

    if all(status == "passed" for status in statuses):
        status = "achieved"
        summary = "all objective criteria passed"
    elif "failed" in statuses:
        status = "not_achieved"
        summary = "at least one objective criterion failed"
    else:
        status = "uncertain"
        summary = "objective could not be fully evaluated from verified evidence"

    # The outcome records the artifacts that establish what was actually
    # observed during the task, not only evidence that happened to satisfy a
    # criterion. This preserves provenance for uncertain/not_achieved outcomes.
    referenced_result_ids = list(result_by_id)
    referenced_evidence_ids = [item.id for item in valid_evidence]

    return Outcome(
        decision_id=decision.id,
        task_id=task.id,
        status=status,
        summary=summary,
        result_ids=referenced_result_ids,
        evidence_ids=referenced_evidence_ids,
    )
