import json
from dataclasses import asdict
from pathlib import Path

from .goals import Goal

GOALS_FILE = Path("goals.json")


def save_goals(goals: list[Goal]) -> None:
    GOALS_FILE.write_text(
        json.dumps([asdict(goal) for goal in goals], indent=2),
        encoding="utf-8",
    )


def load_goals() -> list[Goal]:
    if not GOALS_FILE.exists():
        return []

    data = json.loads(GOALS_FILE.read_text(encoding="utf-8"))
    return [Goal(**item) for item in data]
