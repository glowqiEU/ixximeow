from core.personality import BehaviorAction
from personality_benchmark.evaluator import BenchmarkCandidate, evaluate_case
from pathlib import Path

from personality_benchmark.models import PersonalityBenchmarkCase, load_cases


def test_benchmark_scores_decision_separately_from_tone() -> None:
    case = PersonalityBenchmarkCase(
        id="example-ignore-001",
        status="example_fixture",
        context="an example only; not identity truth",
        incoming="hey",
        relationship_state={"relationship_type": "stranger"},
        expected_actions=(BehaviorAction.IGNORE,),
        acceptable_responses=(),
        unacceptable_responses=("hey babe",),
        expected_boundary_handling="none",
        notes="exercise no-response evaluation",
        no_response=True,
    )

    score = evaluate_case(
        case,
        BenchmarkCandidate(
            action=BehaviorAction.IGNORE,
            response=None,
            boundary_handling="none",
        ),
    )

    assert score.action_match == 1.0
    assert score.no_response_match == 1.0
    assert score.would_send_or_do == 1.0


def test_example_fixture_file_is_machine_readable_and_not_validated_truth() -> None:
    path = (
        Path(__file__).parent.parent
        / "personality_benchmark/fixtures/example_cases.json"
    )
    cases = load_cases(path)

    assert cases
    assert all(case.status == "example_fixture" for case in cases)


def test_would_send_fails_even_when_action_matches_but_tone_does_not() -> None:
    case = PersonalityBenchmarkCase(
        id="example-answer-001",
        status="example_fixture",
        context="synthetic",
        incoming="question",
        relationship_state={},
        expected_actions=(BehaviorAction.ANSWER,),
        acceptable_responses=("answer",),
        unacceptable_responses=(),
        expected_boundary_handling="none",
        notes="synthetic",
        no_response=False,
    )
    score = evaluate_case(
        case,
        BenchmarkCandidate(
            action=BehaviorAction.ANSWER,
            response="answer",
            boundary_handling="none",
            tone_match=0.2,
        ),
    )

    assert score.action_match == 1.0
    assert score.would_send_or_do == 0.0


def test_unacceptable_action_overrides_other_matches() -> None:
    case = PersonalityBenchmarkCase(
        id="example-boundary-001",
        status="example_fixture",
        context="synthetic",
        incoming="request",
        relationship_state={},
        expected_actions=(BehaviorAction.SET_BOUNDARY,),
        acceptable_responses=("no",),
        unacceptable_responses=(),
        expected_boundary_handling="explicit",
        notes="synthetic",
        no_response=False,
        unacceptable_actions=(BehaviorAction.ANSWER,),
        expected_uncertainty=("relationship_low_confidence",),
    )
    score = evaluate_case(
        case,
        BenchmarkCandidate(
            action=BehaviorAction.ANSWER,
            response="no",
            boundary_handling="explicit",
            uncertainty=(),
        ),
    )

    assert score.action_match == 0.0
    assert score.uncertainty_match == 0.0
    assert score.would_send_or_do == 0.0
