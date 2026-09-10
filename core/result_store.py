from uuid import uuid4

from .models import Result
from .persistence import load_record_list, save_json
from .runtime_paths import runtime_file


RESULTS_FILE = runtime_file("results.json")


def save_results(results: list[Result]) -> None:
    save_json(RESULTS_FILE, [result.__dict__ for result in results])


def load_results() -> list[Result]:
    data = load_record_list(RESULTS_FILE)
    return [Result(**item) for item in data]


def ensure_result_id(result: Result) -> Result:
    if result.id is None:
        result.id = str(uuid4())

    return result
