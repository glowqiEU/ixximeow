from dataclasses import dataclass
from enum import Enum

from .personality import FeedbackOutcome, LearningSignal


class LearningAuthority(str, Enum):
    EVIDENCE_CANDIDATE = "evidence_candidate"
    PROPOSED_PREFERENCE = "proposed_preference"


@dataclass(frozen=True)
class LearningPromotionResult:
    authority: LearningAuthority
    lesson: str | None
    unique_signal_count: int
    conflicting_lessons: bool
    can_modify_personality_core: bool = False


class LearningPromotionPolicy:
    def __init__(self, minimum_consistent_signals: int = 3) -> None:
        if minimum_consistent_signals < 2:
            raise ValueError("promotion requires at least two consistent signals")
        self.minimum_consistent_signals = minimum_consistent_signals

    def evaluate(self, signals: list[LearningSignal]) -> LearningPromotionResult:
        unique = {
            signal.id: signal for signal in signals
            if signal.outcome in {FeedbackOutcome.REJECTED, FeedbackOutcome.CORRECTED}
        }
        lessons = {
            signal.inferred_lesson.strip()
            for signal in unique.values()
            if signal.inferred_lesson and signal.inferred_lesson.strip()
        }
        consistent_count = sum(
            1 for signal in unique.values()
            if signal.inferred_lesson and len(lessons) == 1
        )
        promoted = consistent_count >= self.minimum_consistent_signals
        return LearningPromotionResult(
            authority=(
                LearningAuthority.PROPOSED_PREFERENCE
                if promoted else LearningAuthority.EVIDENCE_CANDIDATE
            ),
            lesson=next(iter(lessons)) if len(lessons) == 1 else None,
            unique_signal_count=len(unique),
            conflicting_lessons=len(lessons) > 1,
            can_modify_personality_core=False,
        )
