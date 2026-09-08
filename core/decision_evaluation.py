from dataclasses import dataclass


@dataclass
class DecisionEvaluation:
    decision_id: str
    relevance: float
    confidence: float
    risk: float
    effort: float
    reason: str
