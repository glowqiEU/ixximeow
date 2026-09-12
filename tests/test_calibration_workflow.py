import pytest

from core.calibration import (
    CalibrationCandidate,
    CalibrationFeedback,
    CalibrationWorkflow,
    MirrorRating,
)
from core.personality import BehaviorAction
from core.personality_store import load_learning_signals, save_learning_signals
from personality_benchmark.models import (
    BenchmarkProvenance,
    RealUserBenchmarkCase,
)


def real_case(**overrides) -> RealUserBenchmarkCase:
    values = {
        "id": "real-001",
        "provenance": BenchmarkProvenance.USER_CONFIRMED_REAL_CASE,
        "raw_situation": "buyer asks for a free custom request",
        "incoming": "send it free",
        "platform": "telegram",
        "conversation_context": ("price was already stated",),
        "relationship_context": {
            "relationship_type": "buyer",
            "person_id": "buyer-1",
        },
        "expected_action": BehaviorAction.SET_BOUNDARY,
        "expected_boundary_behavior": "explicit_minimal",
        "no_response": False,
        "ideal_response": "i don't send free",
        "acceptable_alternatives": ("no free requests",),
        "unacceptable_actions": (BehaviorAction.ANSWER,),
        "unacceptable_expressions": ("maybe later babe",),
        "confidence": 0.9,
        "notes": "user supplied",
        "category": "buyers_commercial",
    }
    values.update(overrides)
    return RealUserBenchmarkCase(**values)


def test_end_to_end_not_me_correction_produces_auditable_learning_signal(
    tmp_path,
) -> None:
    workflow = CalibrationWorkflow()
    case = real_case()
    candidates = (
        CalibrationCandidate("a", BehaviorAction.ANSWER, "maybe later babe"),
        CalibrationCandidate("b", BehaviorAction.SET_BOUNDARY, "no free requests"),
    )
    session = workflow.start(case, candidates)
    feedback = CalibrationFeedback(
        case_id=case.id,
        candidate_id="a",
        rating=MirrorRating.NOT_ME,
        selected_best_candidate_id="b",
        correction="i don't send free",
        reason="wrong action and fake intimacy",
        corrected_action=BehaviorAction.SET_BOUNDARY,
        corrected_boundary_behavior="explicit_minimal",
        inferred_lesson="obvious buyer boundary should be minimal",
    )

    result = workflow.submit(session, feedback)

    assert result.signal.case_id == case.id
    assert result.signal.rating == "not_me"
    assert result.signal.context_category == "buyers_commercial"
    assert result.signal.channel == "telegram"
    assert result.signal.relationship_type == "buyer"
    assert result.signal.source_provenance == "user_confirmed_real_case"
    assert result.signal.correction == "i don't send free"
    path = tmp_path / "learning.json"
    save_learning_signals([result.signal], path=path)
    assert load_learning_signals(path=path) == [result.signal]


def test_me_feedback_for_wrong_behavior_is_rejected() -> None:
    workflow = CalibrationWorkflow()
    case = real_case()
    session = workflow.start(
        case,
        (CalibrationCandidate("wrong", BehaviorAction.ANSWER, "sounds natural"),),
    )

    with pytest.raises(ValueError, match="ME rating conflicts"):
        workflow.submit(
            session,
            CalibrationFeedback(
                case_id=case.id,
                candidate_id="wrong",
                rating=MirrorRating.ME,
                reason="natural wording",
            ),
        )


def test_ignore_feedback_cannot_keep_generated_expression() -> None:
    workflow = CalibrationWorkflow()
    case = real_case(
        expected_action=BehaviorAction.IGNORE,
        expected_boundary_behavior="none",
        no_response=True,
        ideal_response=None,
        acceptable_alternatives=(),
    )
    session = workflow.start(
        case,
        (CalibrationCandidate("text", BehaviorAction.ANSWER, "hey"),),
    )
    result = workflow.submit(
        session,
        CalibrationFeedback(
            case_id=case.id,
            candidate_id="text",
            rating=MirrorRating.NOT_ME,
            reason="correct behavior is silence",
            corrected_action=BehaviorAction.IGNORE,
        ),
    )

    assert result.signal.correction is None
    assert result.signal.corrected_action == "ignore"


def test_relationship_and_boundary_corrections_are_preserved() -> None:
    workflow = CalibrationWorkflow()
    case = real_case()
    session = workflow.start(
        case,
        (CalibrationCandidate("a", BehaviorAction.SET_BOUNDARY, "no"),),
    )
    result = workflow.submit(
        session,
        CalibrationFeedback(
            case_id=case.id,
            candidate_id="a",
            rating=MirrorRating.CLOSE,
            reason="relationship was interpreted too warmly",
            corrected_relationship={"relationship_type": "stranger"},
            corrected_boundary_behavior="explicit_minimal",
        ),
    )

    assert result.signal.relationship_correction == {"relationship_type": "stranger"}
    assert result.signal.boundary_correction == "explicit_minimal"


def test_multiple_candidates_can_be_equally_best() -> None:
    workflow = CalibrationWorkflow()
    case = real_case()
    session = workflow.start(
        case,
        (
            CalibrationCandidate("a", BehaviorAction.SET_BOUNDARY, "nieko"),
            CalibrationCandidate("b", BehaviorAction.SET_BOUNDARY, "už 20? nieko"),
        ),
    )
    result = workflow.submit(
        session,
        CalibrationFeedback(
            case_id=case.id,
            candidate_id="a",
            rating=MirrorRating.ME,
            reason="both are me",
            selected_best_candidate_ids=("a", "b"),
        ),
    )

    assert result.signal.selected_best_candidate_ids == ("a", "b")
