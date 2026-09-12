from core.learning_policy import LearningAuthority, LearningPromotionPolicy
from core.personality import FeedbackOutcome, LearningSignal


def signal(identifier: str, lesson: str = "prefer short replies") -> LearningSignal:
    return LearningSignal(
        id=identifier,
        original_input="input",
        candidate="candidate",
        outcome=FeedbackOutcome.CORRECTED,
        correction="shorter",
        reason="too long",
        inferred_lesson=lesson,
    )


def test_single_correction_is_only_evidence_candidate() -> None:
    result = LearningPromotionPolicy(minimum_consistent_signals=3).evaluate(
        [signal("one")]
    )

    assert result.authority is LearningAuthority.EVIDENCE_CANDIDATE
    assert not result.can_modify_personality_core


def test_repeated_corrections_propose_preference_but_never_modify_core() -> None:
    result = LearningPromotionPolicy(minimum_consistent_signals=3).evaluate(
        [signal("one"), signal("two"), signal("three")]
    )

    assert result.authority is LearningAuthority.PROPOSED_PREFERENCE
    assert not result.can_modify_personality_core


def test_duplicate_events_do_not_count_as_repeated_evidence() -> None:
    duplicate = signal("same")
    result = LearningPromotionPolicy(minimum_consistent_signals=2).evaluate(
        [duplicate, duplicate]
    )

    assert result.unique_signal_count == 1
    assert result.authority is LearningAuthority.EVIDENCE_CANDIDATE


def test_contradictory_lessons_do_not_promote() -> None:
    result = LearningPromotionPolicy(minimum_consistent_signals=2).evaluate(
        [signal("one"), signal("two", "prefer long replies")]
    )

    assert result.authority is LearningAuthority.EVIDENCE_CANDIDATE
    assert result.conflicting_lessons
