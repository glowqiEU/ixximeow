from pathlib import Path

from .evidence import Evidence
from .persistence import load_json, save_json


EVIDENCE_FILE = Path("evidence.json")


def save_evidence(evidence: list[Evidence]) -> None:
    save_json(EVIDENCE_FILE, [item.__dict__ for item in evidence])


def load_evidence() -> list[Evidence]:
    data = load_json(EVIDENCE_FILE, [])
    return [Evidence(**item) for item in data]
