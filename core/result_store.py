from pathlib import Path
from typing import Optional

from .file_lock import exclusive_file_lock
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
    """Atomically enforce one result per execution while persisting the result."""
    with exclusive_file_lock(RESULTS_FILE):
        results = load_results()

        for index, existing in enumerate(results):
            if existing.id == result.id:
                results[index] = result
                save_results(results)
                return

        conflicting_result = next(
            (existing for existing in results if existing.execution_id == result.execution_id),
            None,
        )
        if conflicting_result is not None:
            raise ValueError(
                "result execution_id already belongs to another result"
            )

        results.append(result)
        save_results(results)
