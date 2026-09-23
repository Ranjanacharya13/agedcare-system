"""Ranking employees for a shift: SAW for the soft criteria, lexicographic ranking on top."""

import asyncio

from supabase import AsyncClient

from backend.algorithms.lexicographic import rank
from backend.algorithms.saw import calculate_saw_score, normalize_all, saw_breakdown
from backend.models.employee_availability import EmployeeAvailability
from backend.models.employee_shift import EmployeeShift
from backend.repositories.base import SupabaseRepository
from backend.repositories.employee_repository import EmployeeRepository
from backend.schemas.shift_suggestion import ShiftSuggestionOut
from backend.services.availability import group_by_employee, is_available
from backend.services.employee_care_load import get_employee_care_load
from backend.services.risk_scoring import RiskScoringService

# SAW weights (soft criteria only, both are costs: lower is better). Sum to 1.0.
# Same 1.0 : 0.6 balance the old cost model used, scaled to sum to 1.
SHIFT_WEIGHTS = {
    "care_load": 0.625,  # sum of risk scores of residents the employee recently cared for
    "weekly_hours": 0.375,  # hours already worked in the shift's week
}

# Lexicographic priority, most important first: (field, higher_is_better).
# Conflict and role are hard conditions, so they are NOT SAW weights.
SHIFT_PRIORITY = (
    ("conflict", False),  # 1. no overlapping shift first
    ("role_match", True),  # 2. shift's role matches the employee's role
    ("saw_score", True),  # 3. best SAW score
    ("care_load", False),  # 4. tie-break: lower care load
    ("week_hours", False),  # 5. tie-break: fewer weekly hours
)


def role_matches(employee, shift: EmployeeShift) -> bool:
    return not (shift.role and employee.role and str(employee.role) != shift.role)


def rank_shift_candidates(rows: list[dict]) -> list[dict]:
    """rows need: conflict, role_match, care_load, week_hours. Returns them ranked, best first."""
    # Normalise each cost criterion (lower value -> closer to 1).
    care_n = normalize_all([r["care_load"] for r in rows])
    hours_n = normalize_all([r["week_hours"] for r in rows])
    for row, care, hours in zip(rows, care_n, hours_n):
        normalised = {"care_load": care, "weekly_hours": hours}
        # SAW score: higher value means a better candidate.
        row["saw_score"] = calculate_saw_score(normalised, SHIFT_WEIGHTS)
        row["breakdown"] = saw_breakdown(
            normalised,
            SHIFT_WEIGHTS,
            {"care_load": row["care_load"], "weekly_hours": round(row["week_hours"], 2)},
        )
    ranked = rank(rows, SHIFT_PRIORITY)
    for position, row in enumerate(ranked, start=1):
        row["rank"] = position
    return ranked


class ShiftMatchingService:
    def __init__(self, client: AsyncClient, risk_scoring_service: RiskScoringService):
        self._client = client
        self._risk_scoring_service = risk_scoring_service
        self._employee_repository = EmployeeRepository(client)
        self._shift_repository = SupabaseRepository(
            client, "employee_shifts", EmployeeShift, order_column="shift_start",
            parent_field="employee_id",
        )
        self._availability_repository = SupabaseRepository(
            client, "employee_availability", EmployeeAvailability, parent_field="employee_id"
        )

    async def suggest_employees(self, shift_id: str) -> list[ShiftSuggestionOut] | None:
        target = await self._shift_repository.get_by_id(shift_id)
        if target is None:
            return None

        target_week = target.shift_start.isocalendar()[:2]
        employees, availability = await asyncio.gather(
            self._employee_repository.list_all(0, 1000),
            self._availability_repository.list_all(0, 5000),
        )
        availability_by_employee = group_by_employee(availability)

        # Inactive employees, the shift's own holder, and anyone who said they
        # are not available that day are rejected outright.
        candidates = [
            e
            for e in employees
            if e.active
            and e.id != target.employee_id
            and is_available(availability_by_employee.get(str(e.id), []), target.shift_start)
        ]
        rows = await asyncio.gather(
            *(self._build_row(e, target, target_week) for e in candidates)
        )
        return [
            ShiftSuggestionOut(
                employee_id=r["employee"].id,
                first_name=r["employee"].first_name,
                last_name=r["employee"].last_name,
                role=str(r["employee"].role) if r["employee"].role else None,
                current_week_hours=round(r["week_hours"], 2),
                conflict=r["conflict"],
                care_load_score=r["care_load"],
                residents_cared_for_recently=r["residents"],
                role_match=r["role_match"],
                saw_score=round(r["saw_score"], 4),
                rank=r["rank"],
                breakdown=r["breakdown"],
            )
            for r in rank_shift_candidates(list(rows))
        ]

    async def _build_row(self, employee, target, target_week) -> dict:
        other_shifts = await self._shift_repository.list_for_parent(str(employee.id), 0, 200)
        conflict = any(
            s.shift_start < target.shift_end and s.shift_end > target.shift_start
            for s in other_shifts
        )
        week_hours = sum(
            (s.shift_end - s.shift_start).total_seconds() / 3600
            for s in other_shifts
            if s.shift_start.isocalendar()[:2] == target_week
        )
        care_load, residents = await get_employee_care_load(
            str(employee.id), self._client, self._risk_scoring_service
        )
        return {
            "employee": employee,
            "conflict": conflict,
            "role_match": role_matches(employee, target),
            "care_load": care_load,
            "week_hours": week_hours,
            "residents": residents,
        }
