import json
from pathlib import Path

from core.persistence import load_record_list, save_json
from core.personality import BehaviorAction

from .models import BenchmarkProvenance, RealUserBenchmarkCase


def _to_record(case: RealUserBenchmarkCase) -> dict[str, object]:
    return {
        **case.__dict__,
        "provenance": case.provenance.value,
        "expected_action": case.expected_action.value,
        "conversation_context": list(case.conversation_context),
        "acceptable_alternatives": list(case.acceptable_alternatives),
        "unacceptable_actions": [action.value for action in case.unacceptable_actions],
        "unacceptable_expressions": list(case.unacceptable_expressions),
    }


def _from_record(item: dict[str, object]) -> RealUserBenchmarkCase:
    if item.get("provenance") != BenchmarkProvenance.USER_CONFIRMED_REAL_CASE.value:
        raise ValueError("ground-truth store accepts only user-confirmed real cases")
    return RealUserBenchmarkCase(
        **{
            **item,
            "provenance": BenchmarkProvenance(str(item["provenance"])),
            "expected_action": BehaviorAction(str(item["expected_action"])),
            "conversation_context": tuple(item["conversation_context"]),
            "acceptable_alternatives": tuple(item["acceptable_alternatives"]),
            "unacceptable_actions": tuple(
                BehaviorAction(str(action)) for action in item["unacceptable_actions"]
            ),
            "unacceptable_expressions": tuple(item["unacceptable_expressions"]),
        }
    )


def save_real_cases(cases: list[RealUserBenchmarkCase], path: Path) -> None:
    ids = [case.id for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("real benchmark case ids must be unique")
    save_json(path, [_to_record(case) for case in cases])


def load_real_cases(path: Path) -> list[RealUserBenchmarkCase]:
    return [_from_record(item) for item in load_record_list(path)]


def ingest_real_case_json(payload: str) -> RealUserBenchmarkCase:
    try:
        item = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError("invalid real benchmark case JSON") from exc
    if not isinstance(item, dict):
        raise ValueError("real benchmark case must be an object")
    return _from_record(item)
