import json
from pathlib import Path

from .state import SystemState

STATE_FILE = Path("state.json")


def save_state(state: SystemState) -> None:
    STATE_FILE.write_text(
        json.dumps(state.__dict__, indent=2),
        encoding="utf-8",
    )


def load_state() -> SystemState:
    if not STATE_FILE.exists():
        return SystemState()

    data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return SystemState(**data)
