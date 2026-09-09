from .action import Action
from .criterion_evaluator import evaluate_criteria
from .evidence import Evidence
from .execution import Execution
from .models import Decision, Result, Task
from .objective import Objective
from .outcome import Outcome


def verify_execution_result(task: Task, action: Action, execution: Execution, result: Result) -> None:
    """Validate that a technical result belongs to one execution lineage."""
    if action.task_id != task.id:
        raise ValueError("action does not belong to task")
    if execution.task_id != task.id:
        raise ValueError("execution does not belong to task")
    if execution.action_id != action.id:
        raise ValueError("execution does not belong to action")
    if result.task_id != task.id:
        raise ValueError("result does not belong to task")
    if result.action_id != action.id:
        raise ValueError("result does not belong to action")
    if result.execution_id != execution.id:
        raise ValueError("result does not belong to execution")
    if not isinstance(result.success, bool):
        raise ValueError("result success must be a boolean")
    if not result.summary.strip():
        raise ValueError("result summary must not be empty")

    if execution.status == "succeeded" and not result.success:
        raise ValueError("successful execution requires successful result")

    if execution.status == "failed" and result.success:
        raise ValueError("failed execution cannot have successful result")

    if execution.status in {"pending", "running", "uncertain"}:
        raise ValueError(
            f"execution status cannot be verified with a final result: {execution.status}"
        )


def verify_evidence(result: Result, execution: Execution, evidence: Evidence) -> None:
    """Validate that evidence is attached to the result that produced it."""
    if evidence.result_id != result.id:
        raise ValueError("evidence does not belong to result")
    if evidence.execution_id != execution.id:
        raise ValueError("evidence does not belong to execution")


def verify_outcome(
    decision: Decision,
    task: Task,
    objective: Objective,
    results: list[Result],
    evidence: list[Evidence],
    outcome: Outcome,
) -> None:
    """Validate provenance and recompute outcome status from objective criteria."""
    if task.decision_id != decision.id:
        raise ValueError("task does not belong to decision")
    if objective.decision_id != decision.id:
        raise ValueError("objective does not belong to decision")
    if objective.task_id != task.id:
        raise ValueError("objective does not belong to task")
    if outcome.decision_id != decision.id:
        raise ValueError("outcome does not belong to decision")
    if outcome.task_id != task.id:
        raise ValueError("outcome does not belong to task")

    result_by_id = {result.id: result for result in results}
    evidence_by_id = {item.id: item for item in evidence}

    for result_id in outcome.result_ids:
        result = result_by_id.get(result_id)
        if result is None:
            raise ValueError("outcome references unknown result")
        if result.task_id != task.id:
            raise ValueError("outcome references result from another task")

    for evidence_id in outcome.evidence_ids:
        item = evidence_by_id.get(evidence_id)
        if item is None:
            raise ValueError("outcome references unknown evidence")
        result = result_by_id.get(item.result_id)
        if result is None:
            raise ValueError("evidence references unknown result")
        if result.task_id != task.id:
            raise ValueError("outcome references evidence from another task")
        if item.execution_id != result.execution_id:
            raise ValueError("outcome evidence execution does not match result")
        if item.result_id not in outcome.result_ids:
            raise ValueError("outcome evidence must reference a listed result")

    if outcome.status == "blocked":
        if not outcome.block_reason:
            raise ValueError("blocked outcome requires block_reason")
        return

    valid_evidence = [
        item
        for item in evidence
        if item.result_id in result_by_id
        and result_by_id[item.result_id].task_id == task.id
        and item.execution_id == result_by_id[item.result_id].execution_id
    ]
    evaluations = evaluate_criteria(objective.criteria, valid_evidence)
    statuses = [evaluation.status for evaluation in evaluations]

    expected_status = (
        "achieved"
        if all(status == "passed" for status in statuses)
        else "not_achieved"
        if "failed" in statuses
        else "uncertain"
    )

    if outcome.status == "achieved" and not outcome.evidence_ids:
        raise ValueError("achieved outcome requires evidence")
    if not outcome.result_ids and not outcome.evidence_ids:
        raise ValueError("outcome must reference recorded artifacts")
    if outcome.status != expected_status:
        raise ValueError("outcome status does not match deterministic criterion evaluation")
