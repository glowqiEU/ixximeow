from .action import Action
from .action_registry import ActionRegistry
from .evidence import Evidence
from .evidence_store import upsert_evidence
from .execution import Execution
from .execution_store import upsert_execution
from .models import Result
from .result_store import upsert_result


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
        evidence = Evidence(
            result_id=result.id,
            execution_id=execution.id,
            kind="execution_output",
            claim="execution_succeeded",
            value=True,
            content=summary,
            verified=True,
        )
    except Exception as exc:
        execution.transition("failed")
        result = Result(
            task_id=action.task_id,
            action_id=action.id,
            execution_id=execution.id,
            success=False,
            summary=f"action execution failed: {exc}",
        )
        evidence = Evidence(
            result_id=result.id,
            execution_id=execution.id,
            kind="execution_output",
            claim="execution_succeeded",
            value=False,
            content=result.summary,
            verified=True,
        )

    upsert_execution(execution)
    upsert_result(result)
    upsert_evidence(evidence)
    return execution, result, [evidence]
