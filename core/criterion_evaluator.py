from dataclasses import dataclass, field
from typing import Any

from .evidence import Evidence
from .objective import ObjectiveCriterion


CRITERION_EVALUATION_STATUSES = {"passed", "failed", "missing", "conflict"}


@dataclass
class CriterionEvaluation:
    """Deterministic evaluation of one objective criterion."""

    criterion_id: str
    claim: str
    status: str
    evidence_ids: list[str] = field(default_factory=list)
    reason: str = ""

    def __post_init__(self) -> None:
        if not self.criterion_id.strip():
            raise ValueError("criterion evaluation criterion_id cannot be empty")
        if not self.claim.strip():
            raise ValueError("criterion evaluation claim cannot be empty")
        if self.status not in CRITERION_EVALUATION_STATUSES:
            raise ValueError(f"invalid criterion evaluation status: {self.status}")
        if not self.reason.strip():
            raise ValueError("criterion evaluation reason must not be empty")
        if not all(item.strip() for item in self.evidence_ids):
            raise ValueError("criterion evaluation evidence_ids cannot contain empty ids")


def _matches(criterion: ObjectiveCriterion, value: Any) -> bool:
    if criterion.kind == "exists":
        return True
    if criterion.kind == "equals":
        return value == criterion.expected
    if criterion.kind == "boolean":
        return isinstance(value, bool) and value == criterion.expected
    if criterion.kind == "contains":
        if isinstance(value, str):
            return criterion.expected in value
        if isinstance(value, (list, tuple, set)):
            return criterion.expected in value
        if isinstance(value, dict):
            return criterion.expected in value
        return False
    raise ValueError(f"unsupported criterion kind: {criterion.kind}")


def evaluate_criterion(
    criterion: ObjectiveCriterion,
    evidence: list[Evidence],
) -> CriterionEvaluation:
    """Evaluate one criterion using only verified evidence for its claim."""
    matching = [item for item in evidence if item.claim == criterion.claim and item.verified]

    if not matching:
        return CriterionEvaluation(
            criterion_id=criterion.id,
            claim=criterion.claim,
            status="missing",
            reason="no verified evidence exists for this claim",
        )

    if criterion.kind == "exists":
        return CriterionEvaluation(
            criterion_id=criterion.id,
            claim=criterion.claim,
            status="passed",
            evidence_ids=[item.id for item in matching],
            reason="verified evidence exists for the claim",
        )

    values = [item.value for item in matching]
    distinct_values = []
    for value in values:
        if value not in distinct_values:
            distinct_values.append(value)

    if len(distinct_values) > 1:
        return CriterionEvaluation(
            criterion_id=criterion.id,
            claim=criterion.claim,
            status="conflict",
            evidence_ids=[item.id for item in matching],
            reason="verified evidence contains conflicting values",
        )

    passed = _matches(criterion, distinct_values[0])
    return CriterionEvaluation(
        criterion_id=criterion.id,
        claim=criterion.claim,
        status="passed" if passed else "failed",
        evidence_ids=[item.id for item in matching],
        reason=(
            "verified evidence satisfies the criterion"
            if passed
            else "verified evidence does not satisfy the criterion"
        ),
    )


def evaluate_criteria(
    criteria: list[ObjectiveCriterion],
    evidence: list[Evidence],
) -> list[CriterionEvaluation]:
    """Evaluate all objective criteria independently and deterministically."""
    return [evaluate_criterion(criterion, evidence) for criterion in criteria]
