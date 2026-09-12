from dataclasses import dataclass, replace
from typing import Optional

from .personality import (
    BehaviorAction,
    BehaviorDecision,
    BehaviorPolicy,
    DecisionBasis,
    PersonalityCore,
    PersonalityState,
    RelationshipState,
    RelationshipType,
    SituationModel,
)


@dataclass(frozen=True)
class RelationshipActionRule:
    rule_id: str
    relationship_type: RelationshipType
    from_action: BehaviorAction
    to_action: BehaviorAction
    principle: str
    minimum_relationship_confidence: float = 0.5
    minimum_trust: Optional[float] = None
    maximum_entitlement: Optional[float] = None
    maximum_boundary_violations: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.rule_id.strip() or not self.principle.strip():
            raise ValueError("relationship rule id and principle cannot be empty")
        if not 0 <= self.minimum_relationship_confidence <= 1:
            raise ValueError("minimum relationship confidence must be between 0 and 1")
        if self.minimum_trust is not None and not 0 <= self.minimum_trust <= 1:
            raise ValueError("minimum trust must be between 0 and 1")
        if self.maximum_entitlement is not None and not 0 <= self.maximum_entitlement <= 1:
            raise ValueError("maximum entitlement must be between 0 and 1")
        if self.maximum_boundary_violations is not None and self.maximum_boundary_violations < 0:
            raise ValueError("maximum boundary violations cannot be negative")

    def matches(self, relationship: RelationshipState, action: BehaviorAction) -> bool:
        return (
            relationship.confidence >= self.minimum_relationship_confidence
            and relationship.relationship_type is self.relationship_type
            and action is self.from_action
            and (self.minimum_trust is None or relationship.trust >= self.minimum_trust)
            and (
                self.maximum_entitlement is None
                or relationship.entitlement <= self.maximum_entitlement
            )
            and (
                self.maximum_boundary_violations is None
                or relationship.boundary_violations <= self.maximum_boundary_violations
            )
        )


class RelationshipAwarePolicy(BehaviorPolicy):
    """Apply only explicit relationship rules; ships with no personality guesses."""

    def __init__(self, rules: tuple[RelationshipActionRule, ...] = ()) -> None:
        self.rules = rules

    def choose(
        self, situation: SituationModel, relationship: RelationshipState,
        state: PersonalityState, core: PersonalityCore,
    ) -> BehaviorDecision:
        decision = super().choose(situation, relationship, state, core)
        uncertainty = list(decision.basis.uncertainty)
        if relationship.confidence < 0.5:
            uncertainty.append("relationship_low_confidence")
            return replace(
                decision,
                basis=replace(decision.basis, uncertainty=tuple(uncertainty)),
            )
        for rule in self.rules:
            if rule.matches(relationship, decision.action):
                basis = DecisionBasis(
                    situation_signals=decision.basis.situation_signals,
                    relationship_signals=(f"rule:{rule.rule_id}",),
                    personality_principles=(rule.principle,),
                    boundary_state=decision.basis.boundary_state,
                    uncertainty=tuple(uncertainty),
                    chosen_action=rule.to_action,
                )
                return replace(
                    decision,
                    action=rule.to_action,
                    reason="explicit relationship rule changed the behavior",
                    requires_approval=rule.to_action is BehaviorAction.TAKE_ACTION,
                    basis=basis,
                )
        return decision
