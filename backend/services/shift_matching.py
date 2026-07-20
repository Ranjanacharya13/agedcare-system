import asyncio

from supabase import AsyncClient

from backend.models.employee_shift import EmployeeShift
from backend.repositories.base import SupabaseRepository
from backend.repositories.employee_repository import EmployeeRepository
from backend.schemas.shift_suggestion import ShiftSuggestionOut
from backend.services.employee_care_load import get_employee_care_load
from backend.services.risk_scoring import RiskScoringService

# Greedy algorithm: visit every active, role-matching employee once, mark
# whether they already have a time-overlapping shift that week, and rank by
# (1) no conflict first, (2) lowest recent care-load score -- so we don't
# stack more high-risk residents onto someone already covering several --
# then (3) lowest already-scheduled hours that week. Advisory only -- nothing
# is auto-assigned, a human still creates the actual employee_shifts record.


class ShiftMatchingService:
    def __init__(self, client: AsyncClient, risk_scoring_service: RiskScoringService):
        self._client = client
        self._risk_scoring_service = risk_scoring_service
        self._employee_repository = EmployeeRepository(client)
        self._shift_repository = SupabaseRepository(
            client, "employee_shifts", EmployeeShift, order_column="shift_start",
            parent_field="employee_id",
        )

    async def suggest_employees(self, shift_id: str) -> list[ShiftSuggestionOut] | None:
        target = await self._shift_repository.get_by_id(shift_id)
        if target is None:
            return None

        target_week = target.shift_start.isocalendar()[:2]
        employees = await self._employee_repository.list_all(0, 1000)

        candidates = [
            employee
            for employee in employees
            if employee.id != target.employee_id
            and employee.active
            and not (target.role and employee.role and str(employee.role) != target.role)
        ]

        # Each candidate's conflict/hours/care-load lookup is independent, so
        # run them concurrently rather than one at a time -- this loop does
        # several Supabase round-trips per candidate (shift history + a
        # care-load computation that itself scores every recently-touched
        # resident), which adds up fast serially.
        suggestions = await asyncio.gather(
            *(self._build_suggestion(employee, target, target_week) for employee in candidates)
        )

        suggestions = list(suggestions)
        suggestions.sort(key=lambda s: (s.conflict, s.care_load_score, s.current_week_hours))
        return suggestions

    async def _build_suggestion(self, employee, target, target_week) -> ShiftSuggestionOut:
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
        care_load_score, residents_cared_for = await get_employee_care_load(
            str(employee.id), self._client, self._risk_scoring_service
        )
        return ShiftSuggestionOut(
            employee_id=employee.id,
            first_name=employee.first_name,
            last_name=employee.last_name,
            role=str(employee.role) if employee.role else None,
            current_week_hours=round(week_hours, 2),
            conflict=conflict,
            care_load_score=care_load_score,
            residents_cared_for_recently=residents_cared_for,
        )
