import json
from pathlib import Path
from typing import Optional

from .goals import Goal


GOALS_FILE = Path("goals.json")


def save_goals(goals: list[Goal]) -> None:
    GOALS_FILE.write_text(
        json.dumps(
            [goal.__dict__ for goal in goals],
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def load_goals() -> list[Goal]:
    if not GOALS_FILE.exists():
        return []

    data = json.loads(GOALS_FILE.read_text(encoding="utf-8"))
    return [Goal(**item) for item in data]


def get_goal(goal_id: str) -> Optional[Goal]:
    for goal in load_goals():
        if goal.id == goal_id:
            return goal

    return None
