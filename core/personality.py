from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_score(name: str, value: float) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")


class BehaviorAction(str, Enum):
    IGNORE = "ignore"
    WAIT = "wait"
    ACKNOWLEDGE = "acknowledge"
    ANSWER = "answer"
    JOKE = "joke"
    TEASE = "tease"
    HELP = "help"
    PUSH_BACK = "push_back"
    SET_BOUNDARY = "set_boundary"
    ASK = "ask"
    ESCALATE = "escalate"
    TAKE_ACTION = "take_action"


class RelationshipType(str, Enum):
    UNKNOWN = "unknown"
    STRANGER = "stranger"
    AUDIENCE = "audience"
    CUSTOMER = "customer"
    FRIEND = "friend"
    FAMILY = "family"
    COLLABORATOR = "collaborator"
    OWNER = "owner"


class MemoryKind(str, Enum):
    SEMANTIC = "semantic"
    EPISODIC = "episodic"
    RELATIONSHIP = "relationship"
    LEARNED_PREFERENCE = "learned_preference"


class FeedbackOutcome(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CORRECTED = "corrected"


@dataclass(frozen=True)
class PersonalityCore:
    values: tuple[str, ...]
    principles: tuple[str, ...]
    boundaries: tuple[str, ...]
    tendencies: tuple[str, ...]
    identity_source: str = "IDENTITY.md"

    def __post_init__(self) -> None:
        for name in ("values", "principles", "boundaries", "tendencies"):
            if not all(item.strip() for item in getattr(self, name)):
                raise ValueError(f"{name} cannot contain empty values")


@dataclass(frozen=True)
class PersonalityState:
    energy: float = 0.5
    social_battery: float = 0.5
    irritation: float = 0.0
    playfulness: float = 0.5
    curiosity: float = 0.5

    def __post_init__(self) -> None:
        for name in (
            "energy", "social_battery", "irritation", "playfulness", "curiosity"
        ):
            _validate_score(name, getattr(self, name))


@dataclass(frozen=True)
class RelationshipState:
    person_id: str
    relationship_type: RelationshipType = RelationshipType.UNKNOWN
    trust: float = 0.0
    familiarity: float = 0.0
    warmth: float = 0.0
    reliability: float = 0.0
    entitlement: float = 0.0
    boundary_violations: int = 0

    def __post_init__(self) -> None:
        if not self.person_id.strip():
            raise ValueError("person_id cannot be empty")
        for name in ("trust", "familiarity", "warmth", "reliability", "entitlement"):
            _validate_score(name, getattr(self, name))
        if self.boundary_violations < 0:
            raise ValueError("boundary_violations cannot be negative")


@dataclass(frozen=True)
class SituationModel:
    context: str
    incoming: str
    intent: str
    motive: str
    stakes: str
    response_needed: bool
    boundary_required: bool = False
    needs_human_judgment: bool = False
    proposed_action: Optional[BehaviorAction] = None

    def __post_init__(self) -> None:
        if self.stakes not in {"low", "medium", "high"}:
            raise ValueError("stakes must be low, medium, or high")


@dataclass(frozen=True)
class BehaviorDecision:
    action: BehaviorAction
    reason: str
    intent: str
    motive: str
    requires_approval: bool = False
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=_now)


@dataclass(frozen=True)
class Expression:
    decision_id: str
    text: str
    style: str = "ixximeow"

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("expression text cannot be empty")


@dataclass(frozen=True)
class CriticReview:
    passed: bool
    issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class PersonalityMemory:
    kind: MemoryKind
    content: str
    source: str
    person_id: Optional[str] = None
    confidence: float = 0.5
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.content.strip() or not self.source.strip():
            raise ValueError("memory content and source cannot be empty")
        _validate_score("confidence", self.confidence)
        if self.kind is MemoryKind.RELATIONSHIP and not self.person_id:
            raise ValueError("relationship memory requires person_id")


@dataclass(frozen=True)
class LearningSignal:
    original_input: str
    candidate: str
    outcome: FeedbackOutcome
    correction: Optional[str]
    reason: str
    inferred_lesson: Optional[str]
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.original_input.strip() or not self.reason.strip():
            raise ValueError("learning input and reason cannot be empty")
        if self.outcome is FeedbackOutcome.CORRECTED and not self.correction:
            raise ValueError("corrected feedback requires correction")


@dataclass(frozen=True)
class PersonalityPipelineResult:
    decision: BehaviorDecision
    expression: Optional[Expression]
    identity_review: CriticReview
    goal_review: CriticReview
    execution_authorized: bool = False

    @property
    def release_allowed(self) -> bool:
        return (
            self.identity_review.passed
            and self.goal_review.passed
            and not self.decision.requires_approval
        )


class BehaviorPolicy:
    """Choose behavior only from explicit interpreted facts.

    Language interpretation belongs to a future reasoning adapter. This policy is
    deterministic and never performs an external action.
    """

    def choose(self, situation: SituationModel) -> BehaviorDecision:
        if situation.boundary_required:
            action = BehaviorAction.SET_BOUNDARY
            reason = "the interpreted situation requires a boundary"
        elif situation.needs_human_judgment:
            action = BehaviorAction.ESCALATE
            reason = "the situation requires human semantic judgment"
        elif not situation.response_needed:
            action = BehaviorAction.IGNORE
            reason = "the interpreted situation does not require a response"
        elif situation.proposed_action is not None:
            action = situation.proposed_action
            reason = "use the explicitly interpreted behavior proposal"
        else:
            action = BehaviorAction.ACKNOWLEDGE
            reason = "acknowledge when no more specific behavior is justified"

        return BehaviorDecision(
            action=action,
            reason=reason,
            intent=situation.intent,
            motive=situation.motive,
            requires_approval=action is BehaviorAction.TAKE_ACTION,
        )


class IdentityCritic:
    _markers = {
        "scripted": ("thank you for reaching out", "i hope this message finds you"),
        "generic_influencer": ("know your worth", "boss babe", "queen energy"),
        "forced_confidence": ("i'm the prize", "you can't handle me"),
        "forced_humor": ("just kidding lol",),
        "fake_intimacy": ("love you babe", "bestie"),
        "ai_assistant_voice": ("certainly!", "i'd be happy to help"),
        "cringe_slang": ("slay queen", "periodt"),
        "unnecessary_aggression": ("you're pathetic", "idiot"),
        "overexplaining": (),
        "personality_caricature": ("dark feminine", "divine feminine"),
    }

    def review(self, expression: Optional[Expression]) -> CriticReview:
        if expression is None:
            return CriticReview(passed=True)
        lowered = expression.text.lower()
        issues = [
            name for name, markers in self._markers.items()
            if any(marker in lowered for marker in markers)
        ]
        if len(expression.text.split()) > 60:
            issues.append("overexplaining")
        return CriticReview(passed=not issues, issues=tuple(dict.fromkeys(issues)))


class GoalCritic:
    def review(
        self, situation: SituationModel, decision: BehaviorDecision,
        expression: Optional[Expression],
    ) -> CriticReview:
        issues: list[str] = []
        if situation.boundary_required and decision.action is not BehaviorAction.SET_BOUNDARY:
            issues.append("boundary_mismatch")
        if not situation.response_needed and expression is not None:
            issues.append("unnecessary_response")
        if decision.action is BehaviorAction.IGNORE and expression is not None:
            issues.append("ignore_has_expression")
        return CriticReview(passed=not issues, issues=tuple(issues))


class PersonalityDecisionPipeline:
    def __init__(self, core: PersonalityCore) -> None:
        self.core = core
        self.policy = BehaviorPolicy()
        self.identity_critic = IdentityCritic()
        self.goal_critic = GoalCritic()

    def decide(
        self, *, situation: SituationModel, relationship: RelationshipState,
        state: PersonalityState, candidate: Optional[str] = None,
    ) -> PersonalityPipelineResult:
        # Relationship and dynamic state are explicit inputs even where v0.1 has
        # no justified deterministic rule for them. Silent heuristics would turn
        # provisional assumptions into personality truth.
        del relationship, state
        decision = self.policy.choose(situation)
        expression = None
        if decision.action is not BehaviorAction.IGNORE and candidate:
            expression = Expression(decision_id=decision.id, text=candidate)
        identity_review = self.identity_critic.review(expression)
        goal_review = self.goal_critic.review(situation, decision, expression)
        return PersonalityPipelineResult(
            decision=decision,
            expression=expression,
            identity_review=identity_review,
            goal_review=goal_review,
            execution_authorized=False,
        )
