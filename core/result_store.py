from pathlib import Path
from typing import Optional

from .models import Result
from .persistence import load_json, save_json


RESULTS_FILE = Path("results.json")


def save_results(results: list[Result]) -> None:
    save_json(RESULTS_FILE, [result.__dict__ for result in results])


def load_results() -> list[Result]:
    data = load_json(RESULTS_FILE, [])
    return [Result(**item) for item in data]


def find_result_by_id(result_id: str) -> Optional[Result]:
    return next(
        (result for result in load_results() if result.id == result_id),
        None,
    )


def find_result_by_execution_id(execution_id: str) -> Optional[Result]:
    return next(
        (result for result in load_results() if result.execution_id == execution_id),
        None,
    )


def upsert_result(result: Result) -> None:
    results = load_results()
    for index, existing in enumerate(results):
        if existing.id == result.id:
            results[index] = result
            save_results(results)
            return

    results.append(result)
    save_results(results)
