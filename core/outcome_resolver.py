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
    referenced_result_ids = list(
        dict.fromkeys(
            evidence_item.result_id
            for evaluation in evaluations
            for evidence_item in valid_evidence
            if evidence_item.id in evaluation.evidence_ids
        )
    )
    referenced_evidence_ids = list(
        dict.fromkeys(
            evidence_id
            for evaluation in evaluations
            for evidence_id in evaluation.evidence_ids
        )
    )

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

    return Outcome(
        decision_id=decision.id,
        task_id=task.id,
        status=status,
        summary=summary,
        result_ids=referenced_result_ids,
        evidence_ids=referenced_evidence_ids,
    )
