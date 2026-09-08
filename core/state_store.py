from pathlib import Path

from .persistence import load_json, save_json
from .state import SystemState

STATE_FILE = Path("state.json")


def save_state(state: SystemState) -> None:
    save_json(STATE_FILE, state.__dict__)


def load_state() -> SystemState:
    data = load_json(STATE_FILE)
    if data is None:
        return SystemState()

    return SystemState(**data)
