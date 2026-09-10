from typing import Optional

from .goals import Goal
from .persistence import load_json, save_json
from .runtime_paths import runtime_file


GOALS_FILE = runtime_file("goals.json")


def save_goals(goals: list[Goal]) -> None:
    save_json(GOALS_FILE, [goal.__dict__ for goal in goals])


def load_goals() -> list[Goal]:
    data = load_json(GOALS_FILE, [])
    return [Goal(**item) for item in data]


def get_goal(goal_id: str) -> Optional[Goal]:
    for goal in load_goals():
        if goal.id == goal_id:
            return goal

    return None
