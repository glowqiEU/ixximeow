from .action_registry import ActionRegistry
from .orchestrator_v2 import OrchestratorV2


class Orchestrator(OrchestratorV2):
    """Public orchestrator entry point for the explicit lifecycle."""

    def __init__(self, registry: ActionRegistry) -> None:
        super().__init__(registry)
