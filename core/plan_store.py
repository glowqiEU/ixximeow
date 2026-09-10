from .models import Plan
from .persistence import load_json, save_json
from .runtime_paths import runtime_file


PLANS_FILE = runtime_file("plans.json")


def save_plans(plans: list[Plan]) -> None:
    save_json(PLANS_FILE, [plan.__dict__ for plan in plans])


def load_plans() -> list[Plan]:
    data = load_json(PLANS_FILE, [])
    return [Plan(**item) for item in data]


def get_plan(plan_id: str):
    return next((plan for plan in load_plans() if plan.id == plan_id), None)
