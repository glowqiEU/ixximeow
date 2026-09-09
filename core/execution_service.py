from .action import Action
from .action_registry import ActionRegistry
from .evidence import Evidence
from .evidence_store import upsert_evidence
from .execution import Execution
from .execution_store import upsert_execution
from .models import Result
from .result_store import upsert_result


def _build_evidence(
    result: Result,
    execution: Execution,
    output,
    summary: str,
) -> list[Evidence]:
    items = [
        Evidence(
            result_id=result.id,
            execution_id=execution.id,
            kind="execution_output",
            claim="execution_succeeded",
            value=result.success,
            content=summary,
            verified=True,
        )
    ]

    if not isinstance(output, dict):
        return items

    for item in output.get("evidence", []):
        if not isinstance(item, dict):
            raise ValueError("action evidence entries must be dictionaries")
        items.append(
            Evidence(
                result_id=result.id,
                execution_id=execution.id,
                kind=item.get("kind", "execution_output"),
                claim=item["claim"],
                value=item.get("value"),
                content=item["content"],
                source=item.get("source"),
                verified=item.get("verified", False),
            )
        )

    return items


def execute_action(
    action: Action,
    registry: ActionRegistry,
) -> tuple[Execution, Result, list[Evidence]]:
    """Execute one explicit action and persist its technical artifacts."""
    execution = Execution(
        action_id=action.id,
        task_id=action.task_id,
        idempotency_key=action.id,
    )
    execution.transition("running")
    upsert_execution(execution)

    try:
        output = registry.execute(action)
        summary = (
            output.get("summary", "action execution completed")
            if isinstance(output, dict)
            else str(output)
        )
        execution.transition("succeeded")
        result = Result(
            task_id=action.task_id,
            action_id=action.id,
            execution_id=execution.id,
            success=True,
            summary=summary,
        )
        evidence = _build_evidence(result, execution, output, summary)
    except Exception as exc:
        execution.transition("failed")
        result = Result(
            task_id=action.task_id,
            action_id=action.id,
            execution_id=execution.id,
            success=False,
            summary=f"action execution failed: {exc}",
        )
        evidence = _build_evidence(result, execution, None, result.summary)

    upsert_execution(execution)
    upsert_result(result)
    for item in evidence:
        upsert_evidence(item)
    return execution, result, evidence
