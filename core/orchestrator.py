from .context_builder import build_context
from .decision_engine import choose_decision
from .planner import generate_candidates
from .state_manager import apply_decision
from .state_store import save_state
from .task_store import ensure_task_id, load_tasks, save_tasks
from .models import Task
from .state import SystemState


class Orchestrator:
    def run(self):
        context, _ = build_context()

        candidates = generate_candidates(context)
        decision = choose_decision(candidates)

        tasks = load_tasks()

        task = Task(
            title=decision.action,
            decision_id=decision.id,
        )

        task = ensure_task_id(task)
        tasks.append(task)
        save_tasks(tasks)

        state = SystemState(
            active_goal_id=context.goal_id,
            active_task=task.title,
            last_decision_id=decision.id,
            last_result_id=context.last_result_id,
        )

        state = apply_decision(
            state=state,
            decision=decision,
            task=task,
        )

        save_state(state)

        return decision, task
