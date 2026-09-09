from .models import Plan
from .storage import load_json, save_json


PLANS_FILE = "plans.json"


def save_plans(plans):
    save_json(PLANS_FILE, [plan.__dict__ for plan in plans])


def load_plans():
    data = load_json(PLANS_FILE)
    return [Plan(**item) for item in data]


def get_plan(plan_id):
    return next((plan for plan in load_plans() if plan.id == plan_id), None)
