from dataclasses import asdict

from .action import Action
from .persistence import load_record_list, save_json
from .runtime_paths import runtime_file

ACTIONS_FILE = runtime_file("actions.json")


def save_actions(actions: list[Action]) -> None:
    save_json(ACTIONS_FILE, [asdict(action) for action in actions])


def load_actions() -> list[Action]:
    data = load_record_list(ACTIONS_FILE)
    return [Action(**item) for item in data]
