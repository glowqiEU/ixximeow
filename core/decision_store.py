from pathlib import Path

from .models import Decision
from .persistence import load_json, save_json


DECISIONS_FILE = Path("decisions.json")


def save_decisions(decisions: list[Decision]) -> None:
    save_json(DECISIONS_FILE, [decision.__dict__ for decision in decisions])


def load_decisions() -> list[Decision]:
    data = load_json(DECISIONS_FILE, [])
    return [Decision(**item) for item in data]
