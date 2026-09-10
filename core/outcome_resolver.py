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

    missing_criteria = [criterion.name for criterion in objective.criteria]

    # v1 deliberately does not guess semantic matches. Criteria evaluation
    # becomes explicit in the next resolver layer; until then, evidence can
    # establish provenance but not silently prove an objective.
    referenced_result_ids = [item.result_id for item in evidence]
    referenced_evidence_ids = [item.id for item in evidence]

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
