from pathlib import Path

from .evidence import Evidence
from .persistence import load_json, save_json


EVIDENCE_FILE = Path("evidence.json")


def save_evidence(items: list[Evidence]) -> None:
    save_json(EVIDENCE_FILE, [item.__dict__ for item in items])


def load_evidence() -> list[Evidence]:
    data = load_json(EVIDENCE_FILE, [])
    return [Evidence(**item) for item in data]


def upsert_evidence(item: Evidence) -> None:
    items = load_evidence()
    for index, existing in enumerate(items):
        if existing.id == item.id:
            items[index] = item
            save_evidence(items)
            return

    items.append(item)
    save_evidence(items)
