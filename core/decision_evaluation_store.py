from pathlib import Path

from .decision_evaluation import DecisionEvaluation
from .persistence import load_json, save_json


DECISION_EVALUATIONS_FILE = Path("decision_evaluations.json")


def save_decision_evaluations(
    evaluations: list[DecisionEvaluation],
) -> None:
    save_json(
        DECISION_EVALUATIONS_FILE,
        [evaluation.__dict__ for evaluation in evaluations],
    )


def load_decision_evaluations() -> list[DecisionEvaluation]:
    data = load_json(DECISION_EVALUATIONS_FILE, [])
    return [DecisionEvaluation(**item) for item in data]
