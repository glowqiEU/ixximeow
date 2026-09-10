from .persistence import load_record, save_json
from .runtime_paths import runtime_file
from .state import SystemState

STATE_FILE = runtime_file("state.json")


def save_state(state: SystemState) -> None:
    save_json(STATE_FILE, state.__dict__)


def load_state() -> SystemState:
    data = load_record(STATE_FILE)
    if data is None:
        return SystemState()

    return SystemState(**data)
