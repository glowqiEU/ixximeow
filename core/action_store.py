from dataclasses import asdict
from pathlib import Path

from .action import Action
from .persistence import load_json, save_json

ACTIONS_FILE = Path("actions.json")


def save_actions(actions: list[Action]) -> None:
    save_json(ACTIONS_FILE, [asdict(action) for action in actions])


def load_actions() -> list[Action]:
    data = load_json(ACTIONS_FILE, [])
    return [Action(**item) for item in data]
