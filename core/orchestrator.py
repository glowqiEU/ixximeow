from .context_builder import build_context
from .memory_query import build_memory_query
from .decision_evaluator import evaluate_decision
from .decision_evaluation_store import save_decision_evaluations
from .decision_selection import select_decision
from .decision_store import load_decisions, save_decisions
from .planner import generate_candidates
from .plan_builder import build_plan
from .plan_store import load_plans, save_plans
from .state_manager import apply_cancellation, apply_decision, apply_result
from .state_store import load_state, save_state
from .task_store import ensure_task_id, load_tasks, save_tasks
from .executor import execute_task
from .history_store import append_event
from .history import HistoryEvent
from .models import Task
from .approval_gate import check_approval
from .approval_store import load_approvals, save_approvals
from .task_lifecycle import transition_task


class Orchestrator:
    def run(self):
        context = build_context()
        query = build_memory_query(context)
        context = build_context(query=query)

        candidates = generate_candidates(context)
        evaluations = [
            evaluate_decision(candidate, context)
            for candidate in candidates
        ]
        save_decision_evaluations(evaluations)
        decision = select_decision(candidates, evaluations)

        decisions = load_decisions()
        decisions.append(decision)
        save_decisions(decisions)

        plan = build_plan(decision)
        plans = load_plans()
        plans.append(plan)
        save_plans(plans)

        tasks = load_tasks()

        task = Task(
            title=plan.steps[0],
            decision_id=decision.id,
            plan_id=plan.id,
            goal_id=decision.goal_id,
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
            task.approval_id = approval.id
            task = transition_task(task, "waiting_approval")

            tasks[-1] = task
            save_tasks(tasks)

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

        tasks[-1] = task
        save_tasks(tasks)

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

    def resume_approval(self, approval_id: str):
        approvals = load_approvals()
        approval = next(
            (item for item in approvals if item.id == approval_id),
            None,
        )

        if approval is None:
            raise ValueError("approval not found")

        if approval.status not in {"approved", "rejected"}:
            raise ValueError(
                f"approval is not ready to resume: {approval.status}"
            )

        tasks = load_tasks()
        task = next(
            (item for item in tasks if item.id == approval.task_id),
            None,
        )

        if task is None:
            raise ValueError("task for approval not found")

        if task.approval_id != approval.id:
            raise ValueError("approval does not belong to task")

        if task.status != "waiting_approval":
            raise ValueError(
                f"task is not waiting for approval: {task.status}"
            )

        task, result = execute_task(task, approval=approval)

        task_index = next(
            index for index, item in enumerate(tasks) if item.id == task.id
        )
        tasks[task_index] = task
        save_tasks(tasks)
        save_approvals(approvals)

        state = load_state()

        if result is not None:
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
                    decision_id=task.decision_id,
                    task_id=task.id,
                    result_id=result.id,
                )
            )

        else:
            state = apply_cancellation(
                state=state,
                task=task,
            )
            save_state(state)

            append_event(
                HistoryEvent(
                    event_type="task_cancelled",
                    summary="task cancelled after approval rejection",
                    decision_id=task.decision_id,
                    task_id=task.id,
                )
            )

        return task, result
