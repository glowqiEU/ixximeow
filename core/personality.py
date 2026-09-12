from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, Protocol
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


class ResponseDisposition(str, Enum):
    NO_RESPONSE = "no_response"
    WAIT = "wait"
    REPLY_REQUIRED = "reply_required"
    NEEDS_INFORMATION = "needs_information"
    BOUNDARY_RESPONSE = "boundary_response"
    ACTION_PROPOSAL = "action_proposal"
    UNCERTAIN = "uncertain"


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
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if not self.person_id.strip():
            raise ValueError("person_id cannot be empty")
        if not isinstance(self.relationship_type, RelationshipType):
            raise ValueError("relationship_type must be a RelationshipType")
        for name in (
            "trust", "familiarity", "warmth", "reliability", "entitlement",
            "confidence",
        ):
            _validate_score(name, getattr(self, name))
        if self.boundary_violations < 0:
            raise ValueError("boundary_violations cannot be negative")


@dataclass(frozen=True)
class UncertainInference:
    value: str
    confidence: float
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("inference value cannot be empty")
        _validate_score("inference confidence", self.confidence)


@dataclass(frozen=True)
class SituationModel:
    context: str
    incoming: str
    intent: UncertainInference
    motive: UncertainInference
    stakes: str
    response_needed: bool
    boundary_required: bool = False
    needs_human_judgment: bool = False
    proposed_action: Optional[BehaviorAction] = None
    observed_facts: dict[str, Any] = field(default_factory=dict)
    uncertainty: tuple[str, ...] = ()
    response_disposition: Optional[ResponseDisposition] = None
    boundary_confidence: float = 1.0

    def __post_init__(self) -> None:
        if self.stakes not in {"low", "medium", "high"}:
            raise ValueError("stakes must be low, medium, or high")
        if not isinstance(self.intent, UncertainInference):
            raise ValueError("intent must be an uncertain inference")
        if not isinstance(self.motive, UncertainInference):
            raise ValueError("motive must be an uncertain inference")
        if self.proposed_action is not None and not isinstance(
            self.proposed_action, BehaviorAction
        ):
            raise ValueError("proposed_action must be a BehaviorAction")
        _validate_score("boundary confidence", self.boundary_confidence)

    @property
    def intent_value(self) -> str:
        return self.intent.value

    @property
    def motive_value(self) -> str:
        return self.motive.value


@dataclass(frozen=True)
class DecisionBasis:
    situation_signals: tuple[str, ...]
    relationship_signals: tuple[str, ...]
    personality_principles: tuple[str, ...]
    boundary_state: str
    uncertainty: tuple[str, ...]
    chosen_action: BehaviorAction


@dataclass(frozen=True)
class BehaviorDecision:
    action: BehaviorAction
    reason: str
    intent: str
    motive: str
    requires_approval: bool = False
    basis: DecisionBasis = field(
        default_factory=lambda: DecisionBasis((), (), (), "not_required", (), BehaviorAction.ACKNOWLEDGE)
    )
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
    case_id: Optional[str] = None
    rating: Optional[str] = None
    context_category: Optional[str] = None
    relationship_type: Optional[str] = None
    channel: Optional[str] = None
    source_provenance: Optional[str] = None
    evidence_confidence: float = 0.5
    corrected_action: Optional[str] = None
    relationship_correction: Optional[dict[str, Any]] = None
    boundary_correction: Optional[str] = None
    selected_best_candidate_id: Optional[str] = None
    selected_best_candidate_ids: tuple[str, ...] = ()
    candidate_id: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.original_input.strip() or not self.reason.strip():
            raise ValueError("learning input and reason cannot be empty")
        if self.outcome is FeedbackOutcome.CORRECTED and not self.correction:
            has_structured_correction = (
                self.corrected_action is not None
                or self.relationship_correction is not None
                or self.boundary_correction is not None
            )
            if not has_structured_correction:
                raise ValueError("corrected feedback requires correction")
        _validate_score("evidence confidence", self.evidence_confidence)


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


class BehaviorPolicyContract(Protocol):
    def choose(
        self, situation: SituationModel, relationship: RelationshipState,
        state: PersonalityState, core: PersonalityCore,
    ) -> BehaviorDecision: ...


class BehaviorPolicy:
    """Choose behavior only from explicit interpreted facts.

    Language interpretation belongs to a future reasoning adapter. This policy is
    deterministic and never performs an external action.
    """

    def choose(
        self, situation: SituationModel,
        relationship: Optional[RelationshipState] = None,
        state: Optional[PersonalityState] = None,
        core: Optional[PersonalityCore] = None,
    ) -> BehaviorDecision:
        disposition = situation.response_disposition
        boundary_is_uncertain = (
            (situation.boundary_required or disposition is ResponseDisposition.BOUNDARY_RESPONSE)
            and situation.boundary_confidence < 0.5
        )
        if boundary_is_uncertain:
            action = BehaviorAction.WAIT
            reason = "uncertain boundary interpretation fails closed"
        elif situation.boundary_required or disposition is ResponseDisposition.BOUNDARY_RESPONSE:
            action = BehaviorAction.SET_BOUNDARY
            reason = "the interpreted situation requires a boundary"
        elif situation.needs_human_judgment or disposition is ResponseDisposition.UNCERTAIN:
            action = BehaviorAction.WAIT
            reason = "uncertain interpretation fails closed without a response or action"
        elif disposition is ResponseDisposition.WAIT:
            action = BehaviorAction.WAIT
            reason = "the interpreted situation should be revisited later"
        elif disposition is ResponseDisposition.NO_RESPONSE:
            action = BehaviorAction.IGNORE
            reason = "the interpreted situation does not need a response"
        elif disposition is ResponseDisposition.NEEDS_INFORMATION:
            action = BehaviorAction.ASK
            reason = "a safe decision requires more information"
        elif disposition is ResponseDisposition.ACTION_PROPOSAL:
            action = BehaviorAction.TAKE_ACTION
            reason = "the interpreted situation calls for an approval-bound action proposal"
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
            intent=situation.intent_value,
            motive=situation.motive_value,
            requires_approval=action is BehaviorAction.TAKE_ACTION,
            basis=DecisionBasis(
                situation_signals=(f"response_needed:{situation.response_needed}",),
                relationship_signals=(),
                personality_principles=(),
                boundary_state=(
                    f"required:{situation.boundary_confidence}"
                    if situation.boundary_required
                    or disposition is ResponseDisposition.BOUNDARY_RESPONSE
                    else "not_required"
                ),
                uncertainty=situation.uncertainty,
                chosen_action=action,
            ),
        )


class IdentityCritic:
    _markers = {
        "scripted": ("thank you for reaching out", "i hope this message finds you"),
        "generic_influencer": ("know your worth", "boss babe", "queen energy"),
        "forced_confidence": ("i'm the prize", "you can't handle me"),
        "forced_humor": ("just kidding lol",),
        "fake_intimacy": ("love you babe", "bestie"),
        "ai_assistant_voice": ("certainly!", "i'd be happy to help"),
        "excessive_politeness": (
            "thank you so much for your understanding",
            "i sincerely apologize",
        ),
        "cringe_slang": ("slay queen", "periodt"),
        "unnecessary_aggression": ("you're pathetic", "idiot"),
        "overexplaining": (),
        "personality_caricature": ("dark feminine", "divine feminine"),
    }

    def review(
        self, expression: Optional[Expression],
        decision: Optional[BehaviorDecision] = None,
    ) -> CriticReview:
        if expression is None:
            issues = ()
            if decision and decision.basis.chosen_action is not decision.action:
                issues = ("decision_basis_mismatch",)
            return CriticReview(passed=not issues, issues=issues)
        lowered = expression.text.lower()
        issues = [
            name for name, markers in self._markers.items()
            if any(marker in lowered for marker in markers)
        ]
        if len(expression.text.split()) > 60:
            issues.append("overexplaining")
        if decision and decision.basis.chosen_action is not decision.action:
            issues.append("decision_basis_mismatch")
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
        if decision.action is BehaviorAction.WAIT and expression is not None:
            issues.append("wait_has_expression")
        if decision.action is BehaviorAction.TAKE_ACTION and not decision.requires_approval:
            issues.append("action_missing_approval")
        reply_actions = {
            BehaviorAction.ACKNOWLEDGE,
            BehaviorAction.ANSWER,
            BehaviorAction.JOKE,
            BehaviorAction.TEASE,
            BehaviorAction.HELP,
            BehaviorAction.PUSH_BACK,
            BehaviorAction.SET_BOUNDARY,
            BehaviorAction.ASK,
        }
        if decision.action in reply_actions and expression is None:
            issues.append("missing_expression")
        return CriticReview(passed=not issues, issues=tuple(issues))


class PersonalityDecisionPipeline:
    def __init__(
        self, core: PersonalityCore,
        behavior_policy: Optional[BehaviorPolicyContract] = None,
    ) -> None:
        self.core = core
        self.policy = behavior_policy or BehaviorPolicy()
        self.identity_critic = IdentityCritic()
        self.goal_critic = GoalCritic()

    def decide(
        self, *, situation: SituationModel, relationship: RelationshipState,
        state: PersonalityState, candidate: Optional[str] = None,
    ) -> PersonalityPipelineResult:
        decision = self.policy.choose(situation, relationship, state, self.core)
        expression = None
        if decision.action is not BehaviorAction.IGNORE and candidate:
            expression = Expression(decision_id=decision.id, text=candidate)
        identity_review = self.identity_critic.review(expression, decision)
        goal_review = self.goal_critic.review(situation, decision, expression)
        return PersonalityPipelineResult(
            decision=decision,
            expression=expression,
            identity_review=identity_review,
            goal_review=goal_review,
            execution_authorized=False,
        )
