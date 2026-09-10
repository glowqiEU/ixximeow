from pathlib import Path

from .action import Action
from .persistence import load_json, save_json


ACTIONS_FILE = Path("actions.json")


def save_actions(actions: list[Action]) -> None:
    save_json(ACTIONS_FILE, [action.__dict__ for action in actions])


def load_actions() -> list[Action]:
    data = load_json(ACTIONS_FILE, [])
    return [Action(**item) for item in data]


def find_action_by_id(action_id: str) -> Action | None:
    return next((action for action in load_actions() if action.id == action_id), None)


def upsert_action(action: Action) -> None:
    actions = load_actions()
    for index, existing in enumerate(actions):
        if existing.id == action.id:
            actions[index] = action
            save_actions(actions)
            return
    actions.append(action)
    save_actions(actions)
