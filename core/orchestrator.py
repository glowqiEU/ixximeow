from .context_builder import build_context
from .decision_engine import choose_decision
from .planner import generate_candidates
from .state_manager import apply_decision, apply_result
from .state_store import load_state, save_state
from .task_store import ensure_task_id, load_tasks, save_tasks
from .executor import execute_task
from .history_store import append_event
from .history import HistoryEvent
from .models import Task
from .approval_gate import check_approval
from .approval_store import load_approvals, save_approvals


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

        state = load_state()

        state = apply_decision(
            state=state,
            decision=decision,
            task=task,
        )

        approval = check_approval(task)

        if approval is not None:
            task.status = "waiting_approval"

            approvals = load_approvals()
            approvals.append(approval)
            save_approvals(approvals)

            save_state(state)

            append_event(
                HistoryEvent(
                    event_type="approval_requested",
                    summary=approval.reason,
                    decision_id=decision.id,
                    task_id=task.id,
                )
            )

            return decision, task, None

        task, result = execute_task(task)

        state = apply_result(
            state=state,
            task=task,
            result=result,
        )

        save_state(state)

        append_event(
            HistoryEvent(
                event_type="task_executed",
                summary=result.summary,
                decision_id=decision.id,
                task_id=task.id,
                result_id=result.id,
            )
        )

        return decision, task, result
