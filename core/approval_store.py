import json
from dataclasses import asdict
from pathlib import Path

from .approval import Approval

APPROVALS_FILE = Path("approvals.json")


def save_approvals(approvals: list[Approval]) -> None:
    data = [asdict(approval) for approval in approvals]
    APPROVALS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_approvals() -> list[Approval]:
    if not APPROVALS_FILE.exists():
        return []

    data = json.loads(APPROVALS_FILE.read_text(encoding="utf-8"))
    return [Approval(**item) for item in data]
