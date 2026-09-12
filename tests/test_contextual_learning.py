from core.learning_policy import (
    LearningAuthority,
    LearningPromotionPolicy,
    PreferenceScope,
)
from core.personality import FeedbackOutcome, LearningSignal


def signal(
    identifier: str,
    *,
    context: str = "buyers_commercial",
    relationship: str = "buyer",
    channel: str = "telegram",
    provenance: str = "user_confirmed_real_case",
    confidence: float = 0.9,
    lesson: str = "prefer minimal boundary response",
) -> LearningSignal:
    return LearningSignal(
        id=identifier,
        original_input="input",
        candidate="candidate",
        outcome=FeedbackOutcome.CORRECTED,
        correction="no",
        reason="too long",
        inferred_lesson=lesson,
        case_id=f"case-{identifier}",
        rating="not_me",
        context_category=context,
        relationship_type=relationship,
        channel=channel,
        source_provenance=provenance,
        evidence_confidence=confidence,
    )


def test_repeated_buyer_feedback_promotes_contextual_not_global_preference() -> None:
    result = LearningPromotionPolicy(minimum_consistent_signals=3).evaluate(
        [signal("1"), signal("2"), signal("3")]
    )

    assert result.authority is LearningAuthority.PROPOSED_PREFERENCE
    assert result.scope is PreferenceScope.CONTEXTUAL
    assert result.scope_value == "buyers_commercial"
    assert not result.can_modify_personality_core


def test_channel_evidence_cannot_become_global_preference() -> None:
    result = LearningPromotionPolicy(minimum_consistent_signals=2).evaluate(
        [signal("1", channel="x"), signal("2", channel="x")]
    )

    assert result.scope is PreferenceScope.CONTEXTUAL
    assert result.scope is not PreferenceScope.DURABLE_CANDIDATE


def test_relationship_specific_evidence_cannot_become_global_behavior() -> None:
    result = LearningPromotionPolicy(minimum_consistent_signals=2).evaluate(
        [signal("1", relationship="buyer"), signal("2", relationship="buyer")]
    )

    assert result.scope is not PreferenceScope.DURABLE_CANDIDATE


def test_synthetic_and_uncertain_evidence_never_promotes() -> None:
    result = LearningPromotionPolicy(minimum_consistent_signals=2).evaluate(
        [
            signal("1", provenance="example_fixture"),
            signal("2", provenance="inferred_example"),
            signal("3", confidence=0.2),
        ]
    )

    assert result.authority is LearningAuthority.EVIDENCE_CANDIDATE
    assert result.eligible_signal_count == 0


def test_cross_context_evidence_is_still_not_durable_without_approval() -> None:
    result = LearningPromotionPolicy(
        minimum_consistent_signals=3,
        minimum_durable_contexts=3,
        minimum_durable_relationship_types=2,
    ).evaluate(
        [
            signal("1", context="friends", relationship="friend", channel="sms"),
            signal("2", context="buyers", relationship="buyer", channel="telegram"),
            signal("3", context="serious", relationship="family", channel="in_person"),
        ]
    )

    assert result.scope is PreferenceScope.DURABLE_CANDIDATE
    assert result.requires_explicit_approval
    assert not result.can_modify_personality_core
