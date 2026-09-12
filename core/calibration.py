from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from personality_benchmark.models import RealUserBenchmarkCase

from .personality import BehaviorAction, FeedbackOutcome, LearningSignal


class MirrorRating(str, Enum):
    ME = "me"
    CLOSE = "close"
    NOT_ME = "not_me"


@dataclass(frozen=True)
class CalibrationCandidate:
    id: str
    action: BehaviorAction
    expression: Optional[str]

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("candidate id cannot be empty")
        if self.action in {BehaviorAction.IGNORE, BehaviorAction.WAIT}:
            if self.expression is not None:
                raise ValueError("IGNORE and WAIT candidates cannot have expression")
        elif self.expression is None:
            raise ValueError("reply candidate requires expression")


@dataclass(frozen=True)
class CalibrationSession:
    case: RealUserBenchmarkCase
    candidates: tuple[CalibrationCandidate, ...]


@dataclass(frozen=True)
class CalibrationFeedback:
    case_id: str
    candidate_id: str
    rating: MirrorRating
    reason: str
    selected_best_candidate_id: Optional[str] = None
    selected_best_candidate_ids: tuple[str, ...] = ()
    correction: Optional[str] = None
    corrected_action: Optional[BehaviorAction] = None
    corrected_relationship: Optional[dict[str, object]] = None
    corrected_boundary_behavior: Optional[str] = None
    inferred_lesson: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.case_id.strip() or not self.candidate_id.strip():
            raise ValueError("feedback case and candidate ids cannot be empty")
        if not self.reason.strip():
            raise ValueError("feedback reason cannot be empty")
        if not isinstance(self.rating, MirrorRating):
            raise ValueError("feedback rating must be ME, CLOSE, or NOT_ME")


@dataclass(frozen=True)
class CalibrationResult:
    signal: LearningSignal
    selected_candidate: CalibrationCandidate


class CalibrationWorkflow:
    """Mirror Test orchestration with no execution or core-mutation authority."""

    def start(
        self,
        case: RealUserBenchmarkCase,
        candidates: tuple[CalibrationCandidate, ...],
    ) -> CalibrationSession:
        if not candidates:
            raise ValueError("calibration requires at least one candidate")
        ids = [candidate.id for candidate in candidates]
        if len(ids) != len(set(ids)):
            raise ValueError("candidate ids must be unique")
        return CalibrationSession(case=case, candidates=candidates)

    def submit(
        self, session: CalibrationSession, feedback: CalibrationFeedback
    ) -> CalibrationResult:
        if feedback.case_id != session.case.id:
            raise ValueError("feedback case does not match session")
        candidates = {candidate.id: candidate for candidate in session.candidates}
        if feedback.candidate_id not in candidates:
            raise ValueError("feedback candidate not found")
        best_ids = feedback.selected_best_candidate_ids
        if feedback.selected_best_candidate_id is not None:
            best_ids = tuple(dict.fromkeys((*best_ids, feedback.selected_best_candidate_id)))
        if any(candidate_id not in candidates for candidate_id in best_ids):
            raise ValueError("best candidate not found")
        candidate = candidates[feedback.candidate_id]
        case = session.case
        if feedback.rating is MirrorRating.ME:
            if candidate.action is not case.expected_action:
                raise ValueError("ME rating conflicts with expected behavior action")
            if case.no_response != (candidate.expression is None):
                raise ValueError("ME rating conflicts with response requirement")

        corrected_action = feedback.corrected_action
        correction = feedback.correction
        if corrected_action in {BehaviorAction.IGNORE, BehaviorAction.WAIT}:
            correction = None
        corrected = (
            correction is not None
            or corrected_action is not None
            or feedback.corrected_relationship is not None
            or feedback.corrected_boundary_behavior is not None
        )
        if corrected:
            outcome = FeedbackOutcome.CORRECTED
        elif feedback.rating is MirrorRating.ME:
            outcome = FeedbackOutcome.ACCEPTED
        else:
            outcome = FeedbackOutcome.REJECTED
        relationship_type = case.relationship_context.get("relationship_type")
        signal = LearningSignal(
            original_input=case.incoming,
            candidate=candidate.expression or candidate.action.value,
            outcome=outcome,
            correction=correction,
            reason=feedback.reason,
            inferred_lesson=feedback.inferred_lesson,
            case_id=case.id,
            rating=feedback.rating.value,
            context_category=case.category,
            relationship_type=(
                str(relationship_type) if relationship_type is not None else None
            ),
            channel=case.platform,
            source_provenance=case.provenance.value,
            evidence_confidence=case.confidence,
            corrected_action=(corrected_action.value if corrected_action else None),
            relationship_correction=feedback.corrected_relationship,
            boundary_correction=feedback.corrected_boundary_behavior,
            selected_best_candidate_id=feedback.selected_best_candidate_id,
            selected_best_candidate_ids=best_ids,
            candidate_id=feedback.candidate_id,
        )
        return CalibrationResult(signal=signal, selected_candidate=candidate)
