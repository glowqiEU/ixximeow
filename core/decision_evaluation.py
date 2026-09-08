from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class DecisionEvaluation:
    decision_id: str
    relevance: float
    confidence: float
    risk: float
    effort: float
    reason: str
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
