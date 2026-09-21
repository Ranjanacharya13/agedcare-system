"""Demo of SAW + lexicographic ranking. No database needed.

Run from the repo root:  uv run python -m backend.scripts.demo_decision_algorithms
"""

from backend.algorithms.lexicographic import rank
from backend.algorithms.saw import calculate_saw_score, normalize_all

# care_load and weekly_hours are costs (lower is better); skill is a benefit (higher is better).
WEIGHTS = {"care_load": 0.4, "weekly_hours": 0.2, "skill": 0.4}
# Lexicographic priority: (field, higher_is_better). Conflict is NOT a weight.
PRIORITY = (("conflict", False), ("saw_score", True))

employees = [
    {"name": "A", "conflict": False, "care_load": 30, "weekly_hours": 20, "skill": 0.9},
    {"name": "B", "conflict": False, "care_load": 50, "weekly_hours": 15, "skill": 0.7},
    {"name": "C", "conflict": True, "care_load": 10, "weekly_hours": 10, "skill": 1.0},
]

print("STEP 1: normalise each criterion to 0..1 (1 = best)")
columns = {
    "care_load": normalize_all([e["care_load"] for e in employees], benefit=False),
    "weekly_hours": normalize_all([e["weekly_hours"] for e in employees], benefit=False),
    "skill": normalize_all([e["skill"] for e in employees], benefit=True),
}
for i, e in enumerate(employees):
    e["normalised"] = {name: column[i] for name, column in columns.items()}
    print(f"  {e['name']}: " + ", ".join(f"{k}={v:.2f}" for k, v in e["normalised"].items()))

print("\nSTEP 2: weight each criterion (weights sum to 1.0)")
print("  " + ", ".join(f"{k}={v}" for k, v in WEIGHTS.items()))

print("\nSTEP 3: SAW score = sum(weight x normalised)")
for e in employees:
    e["saw_score"] = calculate_saw_score(e["normalised"], WEIGHTS)
    print(f"  {e['name']} = {e['saw_score']:.3f}")

print("\nSTEP 4: lexicographic ranking (no conflict first, then higher SAW score)")
for position, e in enumerate(rank(employees, PRIORITY), start=1):
    note = "  <- best SAW score, but has a schedule conflict" if e["conflict"] else ""
    print(f"  {position}. Employee {e['name']}{note}")

print("\nReason: Employee C had a schedule conflict, which has higher priority than SAW score.")
