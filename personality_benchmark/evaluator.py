from dataclasses import dataclass
from typing import Optional

from core.personality import BehaviorAction
from .models import PersonalityBenchmarkCase


@dataclass(frozen=True)
class BenchmarkCandidate:
    action: BehaviorAction
    response: Optional[str]
    boundary_handling: str
    relationship_match: float = 1.0
    tone_match: float = 1.0
    length_match: float = 1.0
    scriptedness: float = 0.0


@dataclass(frozen=True)
class BenchmarkScore:
    action_match: float
    boundary_match: float
    relationship_match: float
    tone_match: float
    length_match: float
    scriptedness: float
    no_response_match: float
    would_send_or_do: float


def evaluate_case(
    case: PersonalityBenchmarkCase, candidate: BenchmarkCandidate
) -> BenchmarkScore:
    action_match = float(candidate.action in case.expected_actions)
    boundary_match = float(
        candidate.boundary_handling == case.expected_boundary_handling
    )
    no_response_match = float((candidate.response is None) == case.no_response)
    unacceptable = candidate.response in case.unacceptable_responses
    acceptable = (
        case.no_response
        or not case.acceptable_responses
        or candidate.response in case.acceptable_responses
    )
    would_send_or_do = float(
        action_match == 1.0
        and boundary_match == 1.0
        and no_response_match == 1.0
        and acceptable
        and not unacceptable
        and candidate.relationship_match >= 0.8
        and candidate.tone_match >= 0.8
        and candidate.length_match >= 0.8
        and candidate.scriptedness <= 0.2
    )
    return BenchmarkScore(
        action_match=action_match,
        boundary_match=boundary_match,
        relationship_match=candidate.relationship_match,
        tone_match=candidate.tone_match,
        length_match=candidate.length_match,
        scriptedness=candidate.scriptedness,
        no_response_match=no_response_match,
        would_send_or_do=would_send_or_do,
    )
