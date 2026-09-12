from pathlib import Path

from core.personality import BehaviorAction
from personality_benchmark.real_case_store import load_real_cases


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
