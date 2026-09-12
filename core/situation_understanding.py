from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from .personality import (
    BehaviorAction,
    PersonalityState,
    ResponseDisposition,
    SituationModel,
    UncertainInference,
)


KNOWN_PLATFORMS = {
    "x", "instagram", "tiktok", "snapchat", "onlyfans", "telegram",
    "email", "sms", "in_person", "unknown",
}


class InterpretationFailureKind(str, Enum):
    INVALID_MODEL_OUTPUT = "invalid_model_output"
    INTERPRETATION_ERROR = "interpretation_error"


@dataclass(frozen=True)
class InteractionEvent:
    id: str
    content: str

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("interaction event id cannot be empty")


@dataclass(frozen=True)
class RelevantMemory:
    id: str
    content: str
    confidence: float
    contradicts: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.content.strip():
            raise ValueError("memory id and content cannot be empty")
        if not 0 <= self.confidence <= 1:
            raise ValueError("memory confidence must be between 0 and 1")


@dataclass(frozen=True)
class RawInteractionInput:
    incoming_text: str
    platform: str
    personality_state: PersonalityState
    sender_id: Optional[str] = None
    sender_candidates: tuple[str, ...] = ()
    conversation_context: tuple[str, ...] = ()
    recent_history: tuple[InteractionEvent, ...] = ()
    relevant_memory: tuple[RelevantMemory, ...] = ()
    explicit_user_intent: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.incoming_text.strip():
            raise ValueError("incoming_text cannot be empty")
        if not self.platform.strip():
            raise ValueError("platform cannot be empty")


@dataclass(frozen=True)
class InterpretationFailure:
    kind: InterpretationFailureKind
    message: str


@dataclass(frozen=True)
class SituationUnderstandingResult:
    situation: Optional[SituationModel]
    failure: Optional[InterpretationFailure]
    action_authorized: bool = False

    def __post_init__(self) -> None:
        if (self.situation is None) == (self.failure is None):
            raise ValueError("result must contain exactly one of situation or failure")
        if self.action_authorized:
            raise ValueError("situation understanding cannot authorize action")

    @property
    def success(self) -> bool:
        return self.situation is not None and self.failure is None


class SituationUnderstandingAdapter:
    """Validate structured model output without treating inference as observation."""

    _required = {
        "intent", "motive", "stakes", "response_disposition",
        "boundary_required", "boundary_confidence", "proposed_action",
    }

    def interpret(
        self, raw: RawInteractionInput, model_output: dict[str, Any]
    ) -> SituationUnderstandingResult:
        try:
            return SituationUnderstandingResult(
                situation=self._validated_situation(raw, model_output), failure=None
            )
        except (KeyError, TypeError, ValueError) as exc:
            return SituationUnderstandingResult(
                situation=None,
                failure=InterpretationFailure(
                    InterpretationFailureKind.INVALID_MODEL_OUTPUT, str(exc)
                ),
                action_authorized=False,
            )

    def _validated_situation(
        self, raw: RawInteractionInput, output: dict[str, Any]
    ) -> SituationModel:
        if not isinstance(output, dict) or set(output) != self._required:
            raise ValueError("model output has invalid fields")
        intent = self._inference(output["intent"])
        motive = self._inference(output["motive"])
        disposition = output["response_disposition"]
        disposition = ResponseDisposition(disposition)
        if type(output["boundary_required"]) is not bool:
            raise ValueError("boundary_required must be boolean")
        boundary_confidence = output["boundary_confidence"]
        if not isinstance(boundary_confidence, (int, float)) or isinstance(boundary_confidence, bool):
            raise ValueError("boundary_confidence must be numeric")
        if not 0 <= boundary_confidence <= 1:
            raise ValueError("boundary_confidence must be between 0 and 1")

        known_refs = {"incoming_text", "platform", "sender_id", "explicit_user_intent"}
        known_refs.update(f"history:{event.id}" for event in raw.recent_history)
        known_refs.update(f"memory:{memory.id}" for memory in raw.relevant_memory)
        if not set(intent.evidence_refs + motive.evidence_refs) <= known_refs:
            raise ValueError("inference cites unknown evidence")

        uncertainty: list[str] = []
        normalized_platform = raw.platform.lower()
        if normalized_platform not in KNOWN_PLATFORMS:
            uncertainty.append(f"unknown_platform:{raw.platform}")
            normalized_platform = "unknown"
        if raw.sender_id is None:
            uncertainty.append(
                "ambiguous_sender" if len(raw.sender_candidates) > 1 else "unknown_sender"
            )
        elif raw.sender_candidates and raw.sender_id not in raw.sender_candidates:
            uncertainty.append("sender_identity_conflict")
        if intent.confidence < 0.5:
            uncertainty.append("low_intent_confidence")
        if motive.confidence < 0.5:
            uncertainty.append("low_motive_confidence")
        if output["boundary_required"] and boundary_confidence < 0.5:
            uncertainty.append("low_boundary_confidence")
        memory_ids = {memory.id for memory in raw.relevant_memory}
        if any(set(memory.contradicts) & memory_ids for memory in raw.relevant_memory):
            uncertainty.append("contradictory_memory")
        history_ids = [event.id for event in raw.recent_history]
        if len(history_ids) != len(set(history_ids)):
            uncertainty.append("duplicate_history_events")

        action = BehaviorAction(output["proposed_action"])
        needs_human = (
            disposition is ResponseDisposition.UNCERTAIN
            or intent.confidence < 0.5
            or (output["boundary_required"] and boundary_confidence < 0.5)
        )
        if needs_human:
            action = BehaviorAction.WAIT
        response_needed = disposition not in {
            ResponseDisposition.NO_RESPONSE, ResponseDisposition.WAIT,
            ResponseDisposition.UNCERTAIN,
        }
        return SituationModel(
            context="\n".join(raw.conversation_context),
            incoming=raw.incoming_text,
            intent=intent,
            motive=motive,
            stakes=output["stakes"],
            response_needed=response_needed,
            boundary_required=output["boundary_required"],
            needs_human_judgment=needs_human,
            proposed_action=action,
            observed_facts={
                "incoming_text": raw.incoming_text,
                "platform": normalized_platform,
                "sender_id": raw.sender_id,
                "explicit_user_intent": raw.explicit_user_intent,
            },
            uncertainty=tuple(uncertainty),
            response_disposition=disposition,
            boundary_confidence=float(boundary_confidence),
        )

    @staticmethod
    def _inference(value: Any) -> UncertainInference:
        if not isinstance(value, dict) or set(value) != {
            "value", "confidence", "evidence_refs"
        }:
            raise ValueError("inference has invalid fields")
        refs = value["evidence_refs"]
        if not isinstance(value["value"], str):
            raise ValueError("inference value must be a string")
        if not isinstance(value["confidence"], (int, float)) or isinstance(
            value["confidence"], bool
        ):
            raise ValueError("inference confidence must be numeric")
        if not isinstance(refs, list) or any(not isinstance(item, str) for item in refs):
            raise ValueError("evidence_refs must be a string list")
        return UncertainInference(
            value=value["value"],
            confidence=value["confidence"],
            evidence_refs=tuple(refs),
        )
