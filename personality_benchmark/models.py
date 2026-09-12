from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from core.personality import BehaviorAction


@dataclass(frozen=True)
class PersonalityBenchmarkCase:
    id: str
    status: str
    context: str
    incoming: str
    relationship_state: dict[str, Any]
    expected_actions: tuple[BehaviorAction, ...]
    acceptable_responses: tuple[str, ...]
    unacceptable_responses: tuple[str, ...]
    expected_boundary_handling: str
    notes: str
    no_response: bool
    unacceptable_actions: tuple[BehaviorAction, ...] = ()
    expected_uncertainty: tuple[str, ...] = ()
    same_message_group: str | None = None
    correction_lesson: str | None = None

    def __post_init__(self) -> None:
        if self.status not in {"example_fixture", "validated"}:
            raise ValueError("benchmark status must be example_fixture or validated")
        if not self.expected_actions:
            raise ValueError("benchmark case requires an expected action")
        if self.no_response and self.acceptable_responses:
            raise ValueError("no-response case cannot define acceptable responses")


def load_cases(path: Path) -> list[PersonalityBenchmarkCase]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list) or any(not isinstance(item, dict) for item in raw):
        raise ValueError("benchmark file must contain a list of cases")
    return [
        PersonalityBenchmarkCase(
            **{
                **item,
                "expected_actions": tuple(
                    BehaviorAction(action) for action in item["expected_actions"]
                ),
                "acceptable_responses": tuple(item["acceptable_responses"]),
                "unacceptable_responses": tuple(item["unacceptable_responses"]),
                "unacceptable_actions": tuple(
                    BehaviorAction(action)
                    for action in item.get("unacceptable_actions", [])
                ),
                "expected_uncertainty": tuple(item.get("expected_uncertainty", [])),
            }
        )
        for item in raw
    ]
