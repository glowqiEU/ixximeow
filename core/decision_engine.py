from typing import Iterable

from .models import Decision


def choose_decision(options: Iterable[Decision]) -> Decision:
    candidates = list(options)

    if not candidates:
        raise ValueError("no decision options provided")

    return max(candidates, key=lambda decision: decision.priority)
