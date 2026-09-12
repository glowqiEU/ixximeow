from pathlib import Path

from core.personality import BehaviorAction
from personality_benchmark.real_case_store import load_real_cases
from core.personality_store import load_learning_signals


def test_committed_real_dataset_is_valid_and_provenance_safe() -> None:
    path = (
        Path(__file__).parent.parent
        / "personality_benchmark/data/real_cases.json"
    )
    cases = load_real_cases(path)

    assert cases
    assert len({case.id for case in cases}) == len(cases)
    assert all(case.provenance.value == "user_confirmed_real_case" for case in cases)


def test_first_real_case_preserves_confirmed_behavior_without_global_rule() -> None:
    path = (
        Path(__file__).parent.parent
        / "personality_benchmark/data/real_cases.json"
    )
    case = load_real_cases(path)[0]

    assert case.id == "real-snapchat-buyer-lowball-001"
    assert case.expected_action is BehaviorAction.SET_BOUNDARY
    assert case.ideal_response == "nieko"
    assert "Scope is this case only" in case.notes


def test_first_case_feedback_is_persisted_without_global_lesson() -> None:
    path = (
        Path(__file__).parent.parent
        / "personality_benchmark/data/learning_signals.json"
    )
    signals = load_learning_signals(path=path)

    lowball_signals = [
        signal for signal in signals
        if signal.case_id == "real-snapchat-buyer-lowball-001"
    ]
    assert [signal.rating for signal in lowball_signals] == ["me", "me", "not_me"]
    assert all(signal.inferred_lesson is None for signal in lowball_signals)
    assert lowball_signals[0].selected_best_candidate_ids == ("a", "b")


def test_second_case_is_explicit_contrast_not_buyer_globalization() -> None:
    path = (
        Path(__file__).parent.parent
        / "personality_benchmark/data/real_cases.json"
    )
    cases = {case.id: case for case in load_real_cases(path)}
    lowball = cases["real-snapchat-buyer-lowball-001"]
    normal = cases["real-snapchat-potential-buyer-price-002"]

    assert lowball.expected_action is BehaviorAction.SET_BOUNDARY
    assert normal.expected_action is BehaviorAction.ANSWER
    assert normal.expected_boundary_behavior == "none"


def test_second_case_accepts_expression_set_without_single_best() -> None:
    root = Path(__file__).parent.parent / "personality_benchmark/data"
    cases = {case.id: case for case in load_real_cases(root / "real_cases.json")}
    signals = load_learning_signals(path=root / "learning_signals.json")
    case = cases["real-snapchat-potential-buyer-price-002"]
    case_signals = [signal for signal in signals if signal.case_id == case.id]

    assert len(case.acceptable_alternatives) == 3
    assert [signal.rating for signal in case_signals] == ["me", "me", "me"]
    assert all(signal.selected_best_candidate_ids == () for signal in case_signals)
    assert all(signal.inferred_lesson is None for signal in case_signals)


def test_third_case_preserves_calibrated_expression_without_global_lesson() -> None:
    root = Path(__file__).parent.parent / "personality_benchmark/data"
    cases = {case.id: case for case in load_real_cases(root / "real_cases.json")}
    signals = load_learning_signals(path=root / "learning_signals.json")
    case = cases["real-snapchat-stranger-work-provocation-003"]
    case_signals = [signal for signal in signals if signal.case_id == case.id]

    assert case.expected_action is BehaviorAction.JOKE
    assert case.confidence == 1.0
    assert case.ideal_response == "pavydi, nes nedirbsi? 😂"
    assert case.acceptable_alternatives == ()
    assert [signal.rating for signal in case_signals] == ["close", "close", "close"]
    assert all(signal.correction == case.ideal_response for signal in case_signals)
    assert all(signal.inferred_lesson is None for signal in case_signals)
    assert "not a global provocation rule" in case.notes


def test_fourth_case_keeps_warmth_prediction_distinct_from_unsolicited_help() -> None:
    root = Path(__file__).parent.parent / "personality_benchmark/data"
    cases = {case.id: case for case in load_real_cases(root / "real_cases.json")}
    signals = load_learning_signals(path=root / "learning_signals.json")
    case = cases["real-snapchat-known-person-bad-day-004"]

    assert case.expected_action is BehaviorAction.ASK
    assert case.expected_boundary_behavior == "none"
    assert case.relationship_context["relationship_type"] == "known_person_positive"
    assert case.confidence == 0.7
    assert case.ideal_response is None
    assert all(signal.case_id != case.id for signal in signals)
