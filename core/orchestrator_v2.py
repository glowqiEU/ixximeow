from .action import Action
from .action_registry import ActionRegistry
from .action_store import upsert_action
from .approval_gate import check_approval
from .approval_store import load_approvals, save_approvals
from .context_builder import build_context
from .decision_evaluation_store import save_decision_evaluations
from .decision_evaluator import evaluate_decision
from .decision_selection import select_decision
from .decision_store import load_decisions, save_decisions
from .evidence_store import upsert_evidence
from .execution_service import execute_reserved_action, reserve_execution
from .history import HistoryEvent
from .history_store import append_event
from .memory_query import build_memory_query
from .models import Task
from .objective import build_objective
from .outcome_resolver import resolve_outcome
from .outcome_store import upsert_outcome
from .plan_builder import build_plan
from .plan_store import load_plans, save_plans
from .planner import generate_candidates
from .state_manager import apply_decision, apply_result
from .state_store import load_state, save_state
from .task_lifecycle import transition_task
from .task_store import ensure_task_id, load_tasks, save_tasks
from .verification import verify_execution_result, verify_evidence, verify_outcome


class OrchestratorV2:
    """Run the explicit decision-to-outcome lifecycle."""

    def __init__(self, registry: ActionRegistry) -> None:
        self.registry = registry

    def _finalize(self, task, decision, action, execution, state, tasks):
        execution, result, evidence = execute_reserved_action(
            action, execution, self.registry
        )
        verify_execution_result(task, action, execution, result)
        for item in evidence:
            verify_evidence(result, execution, item)
            upsert_evidence(item)

        objective = build_objective(decision, task.id)
        outcome = resolve_outcome(decision, task, objective, [result], evidence)
        verify_outcome(decision, task, objective, [result], evidence, outcome)
        upsert_outcome(outcome)

        if outcome.status == "achieved":
            task = transition_task(task, "completed")
        elif outcome.status == "not_achieved":
            task = transition_task(task, "failed")
        elif outcome.status == "uncertain":
            task = transition_task(task, "uncertain")
        else:
            task = transition_task(task, "blocked")

        task_index = next(index for index, item in enumerate(tasks) if item.id == task.id)
        tasks[task_index] = task
        save_tasks(tasks)

        state = apply_result(state=state, task=task, result=result)
        save_state(state)
        append_event(
            HistoryEvent(
                event_type="task_executed",
                summary=outcome.summary,
                decision_id=decision.id,
                task_id=task.id,
                result_id=result.id,
            )
        )
        return task, result

    def run(self):
        context = build_context()
        context = build_context(query=build_memory_query(context))

        candidates = generate_candidates(context)
        evaluations = [evaluate_decision(candidate, context) for candidate in candidates]
        save_decision_evaluations(evaluations)
        decision = select_decision(candidates, evaluations)

        decisions = load_decisions()
        decisions.append(decision)
        save_decisions(decisions)

        plan = build_plan(decision)
        plans = load_plans()
        plans.append(plan)
        save_plans(plans)

        task = ensure_task_id(
            Task(
                title=plan.steps[0],
                decision_id=decision.id,
                plan_id=plan.id,
                goal_id=decision.goal_id,
            )
        )
        tasks = load_tasks()
        tasks.append(task)
        save_tasks(tasks)

        state = apply_decision(load_state(), decision=decision, task=task)

        action = Action(
            task_id=task.id,
            name=decision.action,
            permission_level=task.required_level,
        )
        upsert_action(action)
        task.action_id = action.id
        tasks[-1] = task
        save_tasks(tasks)

        approval = check_approval(action)
        if approval is not None:
            if approval.action_id != action.id or approval.task_id != task.id:
                raise ValueError("approval does not match action and task")

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

        execution = reserve_execution(action)
        task = transition_task(task, "running")
        tasks[-1] = task
        save_tasks(tasks)
        return self._finalize(task, decision, action, execution, state, tasks)
