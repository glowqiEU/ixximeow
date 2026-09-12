from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
from typing import Any

from core.personality import BehaviorAction


class BenchmarkProvenance(str, Enum):
    USER_CONFIRMED_REAL_CASE = "user_confirmed_real_case"
    EXAMPLE_FIXTURE = "example_fixture"
    INFERRED_EXAMPLE = "inferred_example"


BENCHMARK_CATEGORIES = (
    "casual_friends",
    "buyers_commercial",
    "annoying_boundary_pressure",
    "flirting",
    "soft_caring",
    "serious_discussion",
    "random_observation_humor",
    "conflict",
    "no_response",
    "ambiguous",
)


@dataclass(frozen=True)
class RealUserBenchmarkCase:
    id: str
    provenance: BenchmarkProvenance
    raw_situation: str
    incoming: str
    platform: str
    conversation_context: tuple[str, ...]
    relationship_context: dict[str, Any]
    expected_action: BehaviorAction
    expected_boundary_behavior: str
    no_response: bool
    ideal_response: str | None
    acceptable_alternatives: tuple[str, ...]
    unacceptable_actions: tuple[BehaviorAction, ...]
    unacceptable_expressions: tuple[str, ...]
    confidence: float
    notes: str
    category: str

    def __post_init__(self) -> None:
        if self.provenance is not BenchmarkProvenance.USER_CONFIRMED_REAL_CASE:
            raise ValueError("real-user case requires user_confirmed_real_case provenance")
        if not self.id.strip() or not self.raw_situation.strip():
            raise ValueError("case id and raw situation cannot be empty")
        if not self.platform.strip() or not self.category.strip():
            raise ValueError("platform and category cannot be empty")
        if not isinstance(self.relationship_context, dict):
            raise ValueError("relationship context must be an object")
        string_sequences = (
            self.conversation_context,
            self.acceptable_alternatives,
            self.unacceptable_expressions,
        )
        if any(
            not isinstance(values, tuple)
            or any(not isinstance(value, str) for value in values)
            for values in string_sequences
        ):
            raise ValueError("case text collections must be string tuples")
        if not 0 <= self.confidence <= 1:
            raise ValueError("case confidence must be between 0 and 1")
        if self.no_response:
            if self.expected_action not in {BehaviorAction.IGNORE, BehaviorAction.WAIT}:
                raise ValueError("no-response case must expect IGNORE or WAIT")
            if self.ideal_response is not None or self.acceptable_alternatives:
                raise ValueError("no-response case cannot contain expressions")
        if self.expected_action in self.unacceptable_actions:
            raise ValueError("expected action cannot also be unacceptable")


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
        if self.status not in {"example_fixture", "inferred_example"}:
            raise ValueError(
                "non-real benchmark status must be example_fixture or inferred_example"
            )
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
