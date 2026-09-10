from dataclasses import asdict

from .approval import Approval
from .persistence import load_json, save_json
from .runtime_paths import runtime_file

APPROVALS_FILE = runtime_file("approvals.json")


def save_approvals(approvals: list[Approval]) -> None:
    save_json(APPROVALS_FILE, [asdict(approval) for approval in approvals])


def load_approvals() -> list[Approval]:
    data = load_json(APPROVALS_FILE, [])
    return [Approval(**item) for item in data]
