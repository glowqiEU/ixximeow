from pathlib import Path

from .outcome import Outcome
from .persistence import load_json, save_json


OUTCOMES_FILE = Path("outcomes.json")


def save_outcomes(outcomes: list[Outcome]) -> None:
    save_json(OUTCOMES_FILE, [outcome.__dict__ for outcome in outcomes])


def load_outcomes() -> list[Outcome]:
    data = load_json(OUTCOMES_FILE, [])
    return [Outcome(**item) for item in data]
