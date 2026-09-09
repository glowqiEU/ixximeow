from pathlib import Path

from .outcome import Outcome
from .persistence import load_json, save_json


OUTCOMES_FILE = Path("outcomes.json")


def save_outcomes(outcomes: list[Outcome]) -> None:
    save_json(OUTCOMES_FILE, [outcome.__dict__ for outcome in outcomes])


def load_outcomes() -> list[Outcome]:
    data = load_json(OUTCOMES_FILE, [])
    return [Outcome(**item) for item in data]


def find_outcome_by_id(outcome_id: str) -> Outcome | None:
    return next(
        (outcome for outcome in load_outcomes() if outcome.id == outcome_id),
        None,
    )


def find_outcome_by_task_id(task_id: str) -> Outcome | None:
    return next(
        (outcome for outcome in load_outcomes() if outcome.task_id == task_id),
        None,
    )


def upsert_outcome(outcome: Outcome) -> None:
    outcomes = load_outcomes()
    for index, existing in enumerate(outcomes):
        if existing.id == outcome.id:
            outcomes[index] = outcome
            save_outcomes(outcomes)
            return

    outcomes.append(outcome)
    save_outcomes(outcomes)
