from .models import Decision
from .persistence import load_record_list, save_json
from .runtime_paths import runtime_file


DECISIONS_FILE = runtime_file("decisions.json")


def save_decisions(decisions: list[Decision]) -> None:
    save_json(DECISIONS_FILE, [decision.__dict__ for decision in decisions])


def load_decisions() -> list[Decision]:
    data = load_record_list(DECISIONS_FILE)
    return [Decision(**item) for item in data]
