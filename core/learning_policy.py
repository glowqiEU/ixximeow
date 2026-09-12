from dataclasses import dataclass
from enum import Enum

from .personality import FeedbackOutcome, LearningSignal


class LearningAuthority(str, Enum):
    EVIDENCE_CANDIDATE = "evidence_candidate"
    PROPOSED_PREFERENCE = "proposed_preference"


class PreferenceScope(str, Enum):
    ONE_OFF = "one_off"
    CONTEXTUAL = "contextual"
    RELATIONSHIP = "relationship"
    CHANNEL = "channel"
    DURABLE_CANDIDATE = "durable_candidate"


@dataclass(frozen=True)
class LearningPromotionResult:
    authority: LearningAuthority
    lesson: str | None
    unique_signal_count: int
    conflicting_lessons: bool
    eligible_signal_count: int = 0
    scope: PreferenceScope = PreferenceScope.ONE_OFF
    scope_value: str | None = None
    requires_explicit_approval: bool = False
    can_modify_personality_core: bool = False


class LearningPromotionPolicy:
    def __init__(
        self,
        minimum_consistent_signals: int = 3,
        minimum_durable_contexts: int = 3,
        minimum_durable_relationship_types: int = 2,
    ) -> None:
        if minimum_consistent_signals < 2:
            raise ValueError("promotion requires at least two consistent signals")
        self.minimum_consistent_signals = minimum_consistent_signals
        self.minimum_durable_contexts = minimum_durable_contexts
        self.minimum_durable_relationship_types = minimum_durable_relationship_types

    def evaluate(self, signals: list[LearningSignal]) -> LearningPromotionResult:
        unique = {
            signal.id: signal for signal in signals
            if signal.outcome in {FeedbackOutcome.REJECTED, FeedbackOutcome.CORRECTED}
        }
        eligible = [
            signal for signal in unique.values()
            if signal.source_provenance in {None, "user_confirmed_real_case"}
            and signal.evidence_confidence >= 0.5
        ]
        lessons = {
            signal.inferred_lesson.strip()
            for signal in eligible
            if signal.inferred_lesson and signal.inferred_lesson.strip()
        }
        consistent_count = sum(
            1 for signal in eligible
            if signal.inferred_lesson and len(lessons) == 1
        )
        promoted = consistent_count >= self.minimum_consistent_signals
        contexts = {signal.context_category for signal in eligible if signal.context_category}
        relationships = {
            signal.relationship_type for signal in eligible if signal.relationship_type
        }
        channels = {signal.channel for signal in eligible if signal.channel}
        durable_candidate = (
            promoted
            and len(contexts) >= self.minimum_durable_contexts
            and len(relationships) >= self.minimum_durable_relationship_types
        )
        scope = PreferenceScope.ONE_OFF
        scope_value = None
        if durable_candidate:
            scope = PreferenceScope.DURABLE_CANDIDATE
        elif promoted:
            # Narrowest common evidence dimension wins. This prevents a local
            # pattern from being mislabeled global.
            if len(contexts) == 1:
                scope = PreferenceScope.CONTEXTUAL
                scope_value = next(iter(contexts))
            elif len(relationships) == 1:
                scope = PreferenceScope.RELATIONSHIP
                scope_value = next(iter(relationships))
            elif len(channels) == 1:
                scope = PreferenceScope.CHANNEL
                scope_value = next(iter(channels))
        return LearningPromotionResult(
            authority=(
                LearningAuthority.PROPOSED_PREFERENCE
                if promoted else LearningAuthority.EVIDENCE_CANDIDATE
            ),
            lesson=next(iter(lessons)) if len(lessons) == 1 else None,
            unique_signal_count=len(unique),
            conflicting_lessons=len(lessons) > 1,
            eligible_signal_count=len(eligible),
            scope=scope,
            scope_value=scope_value,
            requires_explicit_approval=durable_candidate,
            can_modify_personality_core=False,
        )
