from pathlib import Path
from typing import Optional

from .evidence import Evidence
from .file_lock import exclusive_file_lock
from .persistence import load_json, save_json


EVIDENCE_FILE = Path("evidence.json")


def save_evidence(items: list[Evidence]) -> None:
    save_json(EVIDENCE_FILE, [item.__dict__ for item in items])


def load_evidence() -> list[Evidence]:
    data = load_json(EVIDENCE_FILE, [])
    return [Evidence(**item) for item in data]


def find_evidence_by_id(evidence_id: str) -> Optional[Evidence]:
    return next(
        (item for item in load_evidence() if item.id == evidence_id),
        None,
    )


def find_evidence_by_result_id(result_id: str) -> list[Evidence]:
    return [item for item in load_evidence() if item.result_id == result_id]


def upsert_evidence(item: Evidence) -> None:
    """Atomically persist one evidence item by evidence identity."""
    with exclusive_file_lock(EVIDENCE_FILE):
        items = load_evidence()
        for index, existing in enumerate(items):
            if existing.id == item.id:
                items[index] = item
                save_evidence(items)
                return

        items.append(item)
        save_evidence(items)
