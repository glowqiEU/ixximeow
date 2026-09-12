from pathlib import Path
from typing import Optional

from .persistence import load_record_list, save_json
from .personality import FeedbackOutcome, LearningSignal, MemoryKind, PersonalityMemory
from .runtime_paths import runtime_file


PERSONALITY_MEMORY_FILE = runtime_file("personality_memory.json")
PERSONALITY_LEARNING_FILE = runtime_file("personality_learning.json")


def save_personality_memories(
    memories: list[PersonalityMemory], *, path: Optional[Path] = None
) -> None:
    target = path or PERSONALITY_MEMORY_FILE
    save_json(target, [{**item.__dict__, "kind": item.kind.value} for item in memories])


def load_personality_memories(
    *, path: Optional[Path] = None
) -> list[PersonalityMemory]:
    target = path or PERSONALITY_MEMORY_FILE
    return [
        PersonalityMemory(**{**item, "kind": MemoryKind(item["kind"])})
        for item in load_record_list(target)
    ]


def save_learning_signals(
    signals: list[LearningSignal], *, path: Optional[Path] = None
) -> None:
    target = path or PERSONALITY_LEARNING_FILE
    save_json(
        target,
        [{**item.__dict__, "outcome": item.outcome.value} for item in signals],
    )


def load_learning_signals(
    *, path: Optional[Path] = None
) -> list[LearningSignal]:
    target = path or PERSONALITY_LEARNING_FILE
    return [
        LearningSignal(
            **{
                **item,
                "outcome": FeedbackOutcome(item["outcome"]),
                "selected_best_candidate_ids": tuple(
                    item.get("selected_best_candidate_ids", [])
                ),
            }
        )
        for item in load_record_list(target)
    ]
