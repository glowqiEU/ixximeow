from .models import Task, Result
from .task_lifecycle import transition_task
from .result_store import load_results, save_results


def execute_task(task: Task) -> tuple[Task, Result]:
    task = transition_task(task, "running")

    try:
        result = Result(
            task_id=task.id,
            success=True,
            summary="task execution completed",
        )

        task = transition_task(task, "completed")

    except Exception as exc:
        result = Result(
            task_id=task.id,
            success=False,
            summary=f"task execution failed: {exc}",
        )

        task = transition_task(task, "failed")

    results = load_results()
    results.append(result)
    save_results(results)

    return task, result
