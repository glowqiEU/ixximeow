import pytest

from core.personality import (
    BehaviorAction,
    PersonalityCore,
    PersonalityDecisionPipeline,
    PersonalityState,
    RelationshipState,
)
from core.situation_understanding import (
    InterpretationFailureKind,
    RawInteractionInput,
    SituationUnderstandingAdapter,
)


def raw(**overrides):
    values = {
        "incoming_text": "can you send it?",
        "platform": "telegram",
        "sender_id": "person-1",
        "personality_state": PersonalityState(),
    }
    values.update(overrides)
    return RawInteractionInput(**values)


def valid_payload(**overrides):
    values = {
        "intent": {
            "value": "request content",
            "confidence": 0.9,
            "evidence_refs": ["incoming_text"],
        },
        "motive": {
            "value": "obtain access",
            "confidence": 0.6,
            "evidence_refs": ["incoming_text"],
        },
        "stakes": "medium",
        "response_disposition": "reply_required",
        "boundary_required": False,
        "boundary_confidence": 0.8,
        "proposed_action": "answer",
    }
    values.update(overrides)
    return values


def test_adapter_preserves_observed_facts_and_labels_inference() -> None:
    result = SituationUnderstandingAdapter().interpret(raw(), valid_payload())

    assert result.success
    assert result.situation is not None
    assert result.situation.observed_facts["incoming_text"] == "can you send it?"
    assert result.situation.intent.value == "request content"
    assert result.situation.intent.confidence == 0.9


def test_low_confidence_intent_fails_closed_to_wait() -> None:
    payload = valid_payload()
    payload["intent"] = {
        "value": "maybe a request",
        "confidence": 0.2,
        "evidence_refs": ["incoming_text"],
    }
    result = SituationUnderstandingAdapter().interpret(raw(), payload)

    assert result.success
    assert result.situation.proposed_action is BehaviorAction.WAIT
    assert result.situation.needs_human_judgment
    assert "low_intent_confidence" in result.situation.uncertainty


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"intent": "free text"},
        valid_payload(stakes="catastrophic"),
        valid_payload(proposed_action="publish_everything"),
    ],
)
def test_malformed_model_output_returns_failure_and_no_situation(payload) -> None:
    result = SituationUnderstandingAdapter().interpret(raw(), payload)

    assert not result.success
    assert result.situation is None
    assert result.failure.kind is InterpretationFailureKind.INVALID_MODEL_OUTPUT
    assert not result.action_authorized


def test_ambiguous_sender_unknown_platform_empty_history_are_representable() -> None:
    result = SituationUnderstandingAdapter().interpret(
        raw(
            platform="new-network",
            sender_id=None,
            sender_candidates=("person-a", "person-b"),
            recent_history=(),
        ),
        valid_payload(),
    )

    assert result.success
    assert result.situation.observed_facts["platform"] == "unknown"
    assert "unknown_platform:new-network" in result.situation.uncertainty
    assert "ambiguous_sender" in result.situation.uncertainty


def test_inference_cannot_cite_unknown_evidence_as_observed_fact() -> None:
    payload = valid_payload()
    payload["intent"] = {
        "value": "request",
        "confidence": 0.8,
        "evidence_refs": ["invented_fact"],
    }
    result = SituationUnderstandingAdapter().interpret(raw(), payload)

    assert not result.success
    assert result.situation is None


@pytest.mark.parametrize(
    ("disposition", "model_action", "expected"),
    [
        ("no_response", "answer", BehaviorAction.IGNORE),
        ("wait", "answer", BehaviorAction.WAIT),
        ("needs_information", "answer", BehaviorAction.ASK),
        ("boundary_response", "answer", BehaviorAction.SET_BOUNDARY),
        ("action_proposal", "answer", BehaviorAction.TAKE_ACTION),
    ],
)
def test_deterministic_policy_owns_disposition_action_mapping(
    disposition, model_action, expected
) -> None:
    understood = SituationUnderstandingAdapter().interpret(
        raw(),
        valid_payload(
            response_disposition=disposition,
            proposed_action=model_action,
        ),
    )
    pipeline = PersonalityDecisionPipeline(PersonalityCore((), (), (), ()))
    result = pipeline.decide(
        situation=understood.situation,
        relationship=RelationshipState(person_id="person-1"),
        state=PersonalityState(),
        candidate=("reply" if expected not in {BehaviorAction.IGNORE, BehaviorAction.WAIT} else None),
    )

    assert result.decision.action is expected
    if expected is BehaviorAction.TAKE_ACTION:
        assert result.decision.requires_approval
        assert not result.execution_authorized


def test_duplicate_history_is_uncertainty_not_repeated_evidence() -> None:
    from core.situation_understanding import InteractionEvent

    result = SituationUnderstandingAdapter().interpret(
        raw(
            recent_history=(
                InteractionEvent("same", "one"),
                InteractionEvent("same", "one"),
            )
        ),
        valid_payload(),
    )

    assert "duplicate_history_events" in result.situation.uncertainty
