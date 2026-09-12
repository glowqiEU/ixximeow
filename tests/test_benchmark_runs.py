from core.personality import BehaviorAction
from personality_benchmark.models import BenchmarkProvenance, RealUserBenchmarkCase
from personality_benchmark.runs import (
    BenchmarkRun,
    RealCasePrediction,
    compare_runs,
    run_real_benchmark,
)


def test_repeated_benchmark_reports_regression_and_improvement() -> None:
    before = BenchmarkRun(
        version="v1",
        scores={"case-a": 0.0, "case-b": 1.0},
    )
    after = BenchmarkRun(
        version="v2",
        scores={"case-a": 1.0, "case-b": 0.0},
    )

    comparison = compare_runs(before, after)

    assert comparison.improved == ("case-a",)
    assert comparison.regressed == ("case-b",)
    assert comparison.net_change == 0.0


def benchmark_case(**overrides):
    values = {
        "id": "case",
        "provenance": BenchmarkProvenance.USER_CONFIRMED_REAL_CASE,
        "raw_situation": "real situation",
        "incoming": "message",
        "platform": "x",
        "conversation_context": (),
        "relationship_context": {},
        "expected_action": BehaviorAction.ANSWER,
        "expected_boundary_behavior": "none",
        "no_response": False,
        "ideal_response": "right words",
        "acceptable_alternatives": (),
        "unacceptable_actions": (),
        "unacceptable_expressions": (),
        "confidence": 1.0,
        "notes": "confirmed",
        "category": "serious_discussion",
    }
    values.update(overrides)
    return RealUserBenchmarkCase(**values)


def test_correct_expression_with_wrong_decision_fails_separately() -> None:
    run = run_real_benchmark(
        "v1",
        [benchmark_case()],
        {"case": RealCasePrediction(BehaviorAction.JOKE, "right words", "none")},
    )

    assert "wrong_behavior_action" in run.failures["case"]
    assert "expression_mismatch" not in run.failures["case"]


def test_correct_decision_with_wrong_expression_fails_separately() -> None:
    run = run_real_benchmark(
        "v1",
        [benchmark_case()],
        {"case": RealCasePrediction(BehaviorAction.ANSWER, "wrong words", "none")},
    )

    assert "wrong_behavior_action" not in run.failures["case"]
    assert "expression_mismatch" in run.failures["case"]


def test_expected_ignore_with_generated_text_is_regression() -> None:
    case = benchmark_case(
        expected_action=BehaviorAction.IGNORE,
        no_response=True,
        ideal_response=None,
    )
    run = run_real_benchmark(
        "v1",
        [case],
        {"case": RealCasePrediction(BehaviorAction.IGNORE, "hey", "none")},
    )

    assert "responded_when_silence_expected" in run.failures["case"]


def test_existing_critics_feed_drift_metrics_without_new_engine() -> None:
    run = run_real_benchmark(
        "v1",
        [benchmark_case()],
        {
            "case": RealCasePrediction(
                BehaviorAction.ANSWER,
                "right words",
                "none",
                identity_issues=("forced_humor", "overexplaining"),
            )
        },
    )

    assert run.drift_counts == {"forced_humor": 1, "overexplaining": 1}
