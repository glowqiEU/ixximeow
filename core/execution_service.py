from typing import Optional

from .action import Action
from .action_registry import ActionRegistry
from .evidence import Evidence
from .evidence_store import find_evidence_by_result_id, upsert_evidence
from .execution import Execution
from .execution_store import find_execution_by_id, find_execution_by_idempotency_key, upsert_execution
from .models import Result
from .reconciliation import Reconciliation
from .result_store import find_result_by_execution_id, upsert_result


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


def reserve_execution(action: Action) -> Execution:
    """Durably reserve one execution attempt without invoking the action."""
    existing = find_execution_by_idempotency_key(action.id)
    if existing is not None:
        if existing.action_id != action.id or existing.task_id != action.task_id:
            raise ValueError("existing execution does not match action")
        if existing.status != "pending":
            raise ValueError(
                f"execution already exists with status: {existing.status}"
            )
        return existing

    execution = Execution(
        action_id=action.id,
        task_id=action.task_id,
        idempotency_key=action.id,
    )
    upsert_execution(execution)
    return execution


def execute_reserved_action(
    action: Action,
    execution: Execution,
    registry: ActionRegistry,
) -> tuple[Execution, Result, list[Evidence]]:
    """Start a pending execution and produce its technical artifacts."""
    if execution.action_id != action.id:
        raise ValueError("execution does not belong to action")
    if execution.task_id != action.task_id:
        raise ValueError("execution does not belong to task")
    if execution.status != "pending":
        raise ValueError(f"execution is not pending: {execution.status}")

    execution.transition("running")
    upsert_execution(execution)

    try:
        output = registry.execute(action)
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
    else:
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

    upsert_execution(execution)
    upsert_result(result)
    for item in evidence:
        upsert_evidence(item)
    return execution, result, evidence


def execute_action(
    action: Action,
    registry: ActionRegistry,
) -> tuple[Execution, Result, list[Evidence]]:
    """Reserve and execute one explicit action."""
    execution = reserve_execution(action)
    return execute_reserved_action(action, execution, registry)


def recover_uncertain_execution(
    execution_id: str,
    action: Action,
    reconciler,
) -> tuple[Execution, Optional[Result], list[Evidence]]:
    """Reconcile an uncertain execution without rerunning the action handler."""
    execution = find_execution_by_id(execution_id)
    if execution is None:
        raise ValueError("execution not found")
    if execution.status != "uncertain":
        raise ValueError(
            f"execution is not uncertain: {execution.status}"
        )
    if execution.action_id != action.id:
        raise ValueError("execution does not belong to action")
    if execution.task_id != action.task_id:
        raise ValueError("execution does not belong to task")

    reconciliation = reconciler(action)
    if not isinstance(reconciliation, Reconciliation):
        raise ValueError("reconciler must return a Reconciliation")

    if reconciliation.status in {"unknown", "not_executed"}:
        return execution, None, []

    if reconciliation.status != "already_succeeded":
        raise ValueError(
            f"invalid reconciliation status: {reconciliation.status}"
        )

    result = find_result_by_execution_id(execution.id)
    if result is None:
        result = Result(
            task_id=action.task_id,
            action_id=action.id,
            execution_id=execution.id,
            success=True,
            summary=f"execution recovered: {reconciliation.summary}",
        )
    else:
        if result.task_id != action.task_id or result.action_id != action.id:
            raise ValueError("existing recovery result does not match execution")
        if not result.success:
            raise ValueError("existing recovery result is not successful")

    evidence = find_evidence_by_result_id(result.id)
    if not evidence:
        evidence = [
            Evidence(
                result_id=result.id,
                execution_id=execution.id,
                kind="verification",
                claim="execution_reconciled",
                value=True,
                content=reconciliation.summary,
                source=reconciliation.source,
                verified=True,
            )
        ]
    else:
        for item in evidence:
            if item.execution_id != execution.id or item.result_id != result.id:
                raise ValueError("existing recovery evidence does not match artifacts")

    upsert_result(result)
    for item in evidence:
        upsert_evidence(item)

    execution.transition("succeeded")
    upsert_execution(execution)
    return execution, result, evidence
