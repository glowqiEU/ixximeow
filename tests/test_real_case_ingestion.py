import json

import pytest

from personality_benchmark.real_case_store import (
    ingest_real_case_json,
    load_real_cases,
    save_real_cases,
)


def record(**overrides):
    values = {
        "id": "real-001",
        "provenance": "user_confirmed_real_case",
        "raw_situation": "someone asked a question",
        "incoming": "question",
        "platform": "telegram",
        "conversation_context": [],
        "relationship_context": {"relationship_type": "friend"},
        "expected_action": "answer",
        "expected_boundary_behavior": "none",
        "no_response": False,
        "ideal_response": "answer",
        "acceptable_alternatives": ["another answer"],
        "unacceptable_actions": ["ignore"],
        "unacceptable_expressions": ["scripted answer"],
        "confidence": 0.9,
        "notes": "confirmed by user",
        "category": "casual_friends",
    }
    values.update(overrides)
    return values


def test_real_case_ingests_and_survives_restart(tmp_path) -> None:
    case = ingest_real_case_json(json.dumps(record()))
    path = tmp_path / "real_cases.json"

    save_real_cases([case], path)
    loaded = load_real_cases(path)

    assert loaded == [case]
    assert loaded[0].provenance.value == "user_confirmed_real_case"


@pytest.mark.parametrize("provenance", ["example_fixture", "inferred_example"])
def test_non_real_provenance_cannot_enter_ground_truth_store(provenance) -> None:
    with pytest.raises(ValueError, match="only user-confirmed"):
        ingest_real_case_json(json.dumps(record(provenance=provenance)))


def test_duplicate_real_cases_cannot_inflate_dataset(tmp_path) -> None:
    case = ingest_real_case_json(json.dumps(record()))

    with pytest.raises(ValueError, match="must be unique"):
        save_real_cases([case, case], tmp_path / "cases.json")
