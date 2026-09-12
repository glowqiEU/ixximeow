import pytest

from core.personality import (
    BehaviorAction,
    PersonalityCore,
    PersonalityDecisionPipeline,
    PersonalityState,
    RelationshipState,
    RelationshipType,
    SituationModel,
)


def build_pipeline() -> PersonalityDecisionPipeline:
    return PersonalityDecisionPipeline(
        core=PersonalityCore(
            values=("selective attention", "real warmth"),
            principles=("silence can be a decision",),
            boundaries=("no unpaid explicit requests",),
            tendencies=("concise", "observant"),
        )
    )


def test_boundary_requirement_wins_before_expression() -> None:
    result = build_pipeline().decide(
        situation=SituationModel(
            context="a request crosses a known boundary",
            incoming="send it free",
            intent="obtain unpaid content",
            motive="access",
            stakes="medium",
            response_needed=True,
            boundary_required=True,
        ),
        relationship=RelationshipState(
            person_id="person-1",
            relationship_type=RelationshipType.CUSTOMER,
            entitlement=0.8,
            boundary_violations=2,
        ),
        state=PersonalityState(irritation=0.4),
        candidate="i don't send explicit content for free",
    )

    assert result.decision.action is BehaviorAction.SET_BOUNDARY
    assert result.expression is not None
    assert result.goal_review.passed


def test_no_response_is_a_first_class_decision() -> None:
    result = build_pipeline().decide(
        situation=SituationModel(
            context="low-value message",
            incoming="hey",
            intent="unknown",
            motive="unknown",
            stakes="low",
            response_needed=False,
        ),
        relationship=RelationshipState(person_id="person-2"),
        state=PersonalityState(energy=0.2, social_battery=0.1),
        candidate="hey",
    )

    assert result.decision.action is BehaviorAction.IGNORE
    assert result.expression is None
    assert result.identity_review.passed


def test_take_action_is_only_a_proposal_and_requires_approval() -> None:
    result = build_pipeline().decide(
        situation=SituationModel(
            context="external action requested",
            incoming="post this",
            intent="publish",
            motive="share content",
            stakes="high",
            response_needed=True,
            proposed_action=BehaviorAction.TAKE_ACTION,
        ),
        relationship=RelationshipState(person_id="owner"),
        state=PersonalityState(),
        candidate="ready to post",
    )

    assert result.decision.action is BehaviorAction.TAKE_ACTION
    assert result.decision.requires_approval
    assert not result.execution_authorized
    assert not result.release_allowed


def test_identity_and_goal_critics_are_independent_release_gates() -> None:
    result = build_pipeline().decide(
        situation=SituationModel(
            context="answer is useful",
            incoming="can you help?",
            intent="request help",
            motive="solve a problem",
            stakes="low",
            response_needed=True,
            proposed_action=BehaviorAction.HELP,
        ),
        relationship=RelationshipState(person_id="person-3"),
        state=PersonalityState(),
        candidate="Certainly! I'd be happy to help",
    )

    assert not result.identity_review.passed
    assert result.goal_review.passed
    assert not result.release_allowed


def test_models_reject_invalid_normalized_scores() -> None:
    with pytest.raises(ValueError, match="energy"):
        PersonalityState(energy=1.1)
