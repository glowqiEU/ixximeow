from dataclasses import dataclass

from core.personality import BehaviorAction
from .models import RealUserBenchmarkCase


@dataclass(frozen=True)
class RealCasePrediction:
    action: BehaviorAction
    expression: str | None
    boundary_behavior: str
    identity_issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class BenchmarkRun:
    version: str
    scores: dict[str, float]
    failures: dict[str, tuple[str, ...]] | None = None
    drift_counts: dict[str, int] | None = None


@dataclass(frozen=True)
class BenchmarkComparison:
    improved: tuple[str, ...]
    regressed: tuple[str, ...]
    unchanged: tuple[str, ...]
    net_change: float


def compare_runs(before: BenchmarkRun, after: BenchmarkRun) -> BenchmarkComparison:
    common = sorted(set(before.scores) & set(after.scores))
    improved = tuple(case for case in common if after.scores[case] > before.scores[case])
    regressed = tuple(case for case in common if after.scores[case] < before.scores[case])
    unchanged = tuple(case for case in common if after.scores[case] == before.scores[case])
    net_change = sum(after.scores[case] - before.scores[case] for case in common)
    return BenchmarkComparison(improved, regressed, unchanged, net_change)


def run_real_benchmark(
    version: str,
    cases: list[RealUserBenchmarkCase],
    predictions: dict[str, RealCasePrediction],
) -> BenchmarkRun:
    scores: dict[str, float] = {}
    failures: dict[str, tuple[str, ...]] = {}
    drift_counts: dict[str, int] = {}
    for case in cases:
        prediction = predictions.get(case.id)
        if prediction is None:
            scores[case.id] = 0.0
            failures[case.id] = ("missing_prediction",)
            continue
        issues: list[str] = []
        if prediction.action is not case.expected_action:
            issues.append("wrong_behavior_action")
        if prediction.action in case.unacceptable_actions:
            issues.append("unacceptable_behavior_action")
        if prediction.boundary_behavior != case.expected_boundary_behavior:
            issues.append("wrong_boundary_behavior")
        if case.no_response and prediction.expression is not None:
            issues.append("responded_when_silence_expected")
        if not case.no_response and prediction.expression is None:
            issues.append("missing_expression")
        accepted_expressions = set(case.acceptable_alternatives)
        if case.ideal_response is not None:
            accepted_expressions.add(case.ideal_response)
        if (
            prediction.expression is not None
            and accepted_expressions
            and prediction.expression not in accepted_expressions
        ):
            issues.append("expression_mismatch")
        if prediction.expression in case.unacceptable_expressions:
            issues.append("unacceptable_expression")
        issues.extend(prediction.identity_issues)
        for issue in prediction.identity_issues:
            drift_counts[issue] = drift_counts.get(issue, 0) + 1
        failures[case.id] = tuple(dict.fromkeys(issues))
        scores[case.id] = float(not issues)
    return BenchmarkRun(version, scores, failures, drift_counts)
