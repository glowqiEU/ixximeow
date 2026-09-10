from .evidence import Evidence
from .models import Result


def record_evidence(
    result: Result,
    *,
    kind: str,
    content: str,
) -> Evidence:
    """Record an observation with provenance derived from an execution result.

    Recording evidence does not verify it. Verification is a separate concern.
    """
    if result.id is None or not result.id.strip():
        raise ValueError("result must have an id to record evidence")
    if result.execution_id is None or not result.execution_id.strip():
        raise ValueError("result must have an execution_id to record evidence")
    if not kind.strip():
        raise ValueError("evidence kind cannot be empty")
    if not content.strip():
        raise ValueError("evidence content cannot be empty")

    return Evidence(
        result_id=result.id,
        execution_id=result.execution_id,
        kind=kind,
        content=content,
        verified=False,
    )
