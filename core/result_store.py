import json
from pathlib import Path
from uuid import uuid4

from .models import Result


RESULTS_FILE = Path("results.json")


def save_results(results: list[Result]) -> None:
    RESULTS_FILE.write_text(
        json.dumps([result.__dict__ for result in results], indent=2),
        encoding="utf-8",
    )


def load_results() -> list[Result]:
    if not RESULTS_FILE.exists():
        return []

    data = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    return [Result(**item) for item in data]


def ensure_result_id(result: Result) -> Result:
    if result.id is None:
        result.id = str(uuid4())

    return result
