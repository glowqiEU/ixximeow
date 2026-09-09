from .action import Action
from .evidence import Evidence
from .execution import Execution
from .models import Decision, Result, Task
from .outcome import Outcome


def verify_execution_result(
    task: Task,
    action: Action,
    execution: Execution,
    result: Result,
) -> None:
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


def verify_evidence(
    result: Result,
    execution: Execution,
    evidence: Evidence,
) -> None:
    """Validate that evidence is attached to the result that produced it."""
    if evidence.result_id != result.id:
        raise ValueError("evidence does not belong to result")

    if evidence.execution_id != execution.id:
        raise ValueError("evidence does not belong to execution")


def verify_outcome(
    decision: Decision,
    task: Task,
    results: list[Result],
    evidence: list[Evidence],
    outcome: Outcome,
) -> None:
    """Validate that an objective outcome is supported by recorded artifacts."""
    if task.decision_id != decision.id:
        raise ValueError("task does not belong to decision")

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
