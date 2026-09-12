from core.personality import (
    BehaviorAction,
    PersonalityCore,
    PersonalityDecisionPipeline,
    PersonalityState,
    RelationshipState,
    RelationshipType,
    SituationModel,
    UncertainInference,
)
from core.relationship_policy import RelationshipActionRule, RelationshipAwarePolicy


def situation() -> SituationModel:
    return SituationModel(
        context="same synthetic message",
        incoming="are you coming?",
        intent=UncertainInference("request answer", 0.9, ("incoming_text",)),
        motive=UncertainInference("coordinate", 0.8, ("incoming_text",)),
        stakes="low",
        response_needed=True,
        proposed_action=BehaviorAction.ANSWER,
        observed_facts={"incoming_text": "are you coming?"},
    )


def pipeline() -> PersonalityDecisionPipeline:
    policy = RelationshipAwarePolicy(
        rules=(
            RelationshipActionRule(
                rule_id="synthetic-friend-wait",
                relationship_type=RelationshipType.FRIEND,
                from_action=BehaviorAction.ANSWER,
                to_action=BehaviorAction.WAIT,
                principle="synthetic benchmark rule; not personality truth",
            ),
        )
    )
    return PersonalityDecisionPipeline(
        core=PersonalityCore((), (), (), ()), behavior_policy=policy
    )


def test_same_message_can_choose_different_actions_by_relationship() -> None:
    stranger = pipeline().decide(
        situation=situation(),
        relationship=RelationshipState(
            person_id="s", relationship_type=RelationshipType.STRANGER
        ),
        state=PersonalityState(),
        candidate="yes",
    )
    friend = pipeline().decide(
        situation=situation(),
        relationship=RelationshipState(
            person_id="f", relationship_type=RelationshipType.FRIEND
        ),
        state=PersonalityState(),
    )

    assert stranger.decision.action is BehaviorAction.ANSWER
    assert friend.decision.action is BehaviorAction.WAIT
    assert friend.decision.basis.relationship_signals == (
        "rule:synthetic-friend-wait",
    )


def test_partial_low_confidence_relationship_does_not_trigger_rule() -> None:
    result = pipeline().decide(
        situation=situation(),
        relationship=RelationshipState(
            person_id="uncertain",
            relationship_type=RelationshipType.FRIEND,
            confidence=0.2,
        ),
        state=PersonalityState(),
        candidate="yes",
    )

    assert result.decision.action is BehaviorAction.ANSWER
    assert "relationship_low_confidence" in result.decision.basis.uncertainty


def test_ambiguous_sender_prevents_relationship_rule() -> None:
    uncertain_situation = situation()
    uncertain_situation = SituationModel(
        **{**uncertain_situation.__dict__, "uncertainty": ("ambiguous_sender",)}
    )
    result = pipeline().decide(
        situation=uncertain_situation,
        relationship=RelationshipState(
            person_id="candidate", relationship_type=RelationshipType.FRIEND
        ),
        state=PersonalityState(),
        candidate="yes",
    )

    assert result.decision.action is BehaviorAction.ANSWER
    assert result.decision.basis.relationship_signals == ()


def test_relationship_rule_cannot_weaken_boundary() -> None:
    import pytest

    with pytest.raises(ValueError, match="cannot weaken"):
        RelationshipActionRule(
            rule_id="unsafe",
            relationship_type=RelationshipType.FRIEND,
            from_action=BehaviorAction.SET_BOUNDARY,
            to_action=BehaviorAction.TEASE,
            principle="synthetic unsafe rule",
        )
