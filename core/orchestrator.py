from .context_builder import build_context
from .decision_engine import choose_decision
from .planner import generate_candidates
from .state_manager import apply_decision
from .state_store import save_state
from .task_store import ensure_task_id, load_tasks, save_tasks
from .executor import execute_task
from .history_store import append_event
from .history import HistoryEvent
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

        task, result = execute_task(task)

        state = SystemState(
            active_goal_id=context.goal_id,
            active_task=task.title,
            last_decision_id=decision.id,
            last_result_id=result.id,
        )

        state = apply_decision(
            state=state,
            decision=decision,
            task=task,
        )

        save_state(state)

        append_event(HistoryEvent(event_type="task_executed", summary=result.summary, decision_id=decision.id, task_id=task.id, result_id=result.id))

        return decision, task, result
