from .outcome import Outcome
from .persistence import load_record_list, save_json
from .runtime_paths import runtime_file


OUTCOMES_FILE = runtime_file("outcomes.json")


def save_outcomes(outcomes: list[Outcome]) -> None:
    save_json(OUTCOMES_FILE, [outcome.__dict__ for outcome in outcomes])


def load_outcomes() -> list[Outcome]:
    data = load_record_list(OUTCOMES_FILE)
    return [Outcome(**item) for item in data]
