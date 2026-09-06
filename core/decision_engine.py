from typing import Iterable
from uuid import uuid4

from .models import Decision


def choose_decision(options: Iterable[Decision]) -> Decision:
    candidates = list(options)

    if not candidates:
        raise ValueError("no decision options provided")

    decision = max(candidates, key=lambda item: item.priority)

    if decision.id is None:
        decision.id = str(uuid4())

    return decision
