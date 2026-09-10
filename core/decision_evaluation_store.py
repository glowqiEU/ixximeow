from .decision_evaluation import DecisionEvaluation
from .persistence import load_record_list, save_json
from .runtime_paths import runtime_file


DECISION_EVALUATIONS_FILE = runtime_file("decision_evaluations.json")


def save_decision_evaluations(
    evaluations: list[DecisionEvaluation],
) -> None:
    save_json(
        DECISION_EVALUATIONS_FILE,
        [evaluation.__dict__ for evaluation in evaluations],
    )


def load_decision_evaluations() -> list[DecisionEvaluation]:
    data = load_record_list(DECISION_EVALUATIONS_FILE)
    return [DecisionEvaluation(**item) for item in data]
