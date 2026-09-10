from typing import Optional

from .evidence import Evidence
from .objective import ObjectiveCriterion


_TRUE_VALUES = {"true"}
_FALSE_VALUES = {"false"}


def _verified(evidence: list[Evidence]) -> list[Evidence]:
    return [item for item in evidence if item.verified]


def evaluate_criterion(
    criterion: ObjectiveCriterion,
    evidence: list[Evidence],
) -> Optional[bool]:
    """Evaluate one criterion conservatively from verified evidence.

    Returns True when the criterion is explicitly supported, False only when
    explicit boolean evidence contradicts the expected value, and None when
    the available evidence is insufficient to decide.
    """
    verified = _verified(evidence)
    if not verified:
        return None

    if criterion.kind == "exists":
        return True

    if criterion.kind == "contains":
        expected = str(criterion.expected)
        if any(expected in item.content for item in verified):
            return True
        return None

    if criterion.kind == "equals":
        expected = str(criterion.expected)
        if any(item.content == expected for item in verified):
            return True
        return None

    if criterion.kind == "boolean":
        expected = bool(criterion.expected)
        values = {
            item.content.strip().lower()
            for item in verified
            if item.content.strip().lower() in _TRUE_VALUES | _FALSE_VALUES
        }
        if expected and "true" in values:
            return True
        if not expected and "false" in values:
            return True
        if expected and "false" in values and "true" not in values:
            return False
        if not expected and "true" in values and "false" not in values:
            return False
        return None

    raise ValueError(f"unsupported criterion kind: {criterion.kind}")
