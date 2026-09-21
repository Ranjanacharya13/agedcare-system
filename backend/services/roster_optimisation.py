"""SAW-based roster recommendation (endpoint name kept: POST /roster/optimise).

Not a globally optimal roster. Shifts are handled one at a time, earliest first. For each
shift every active employee is ranked with SAW + lexicographic ranking (see shift_matching.py)
and the best one without a conflict is recommended. Each recommendation is remembered, so the
same employee is never recommended for two overlapping shifts.
"""

from __future__ import annotations

import asyncio
from datetime import datetime

from supabase import AsyncClient

from backend.models.employee import Employee
from backend.models.employee_shift import EmployeeShift
from backend.repositories.base import SupabaseRepository
from backend.repositories.employee_repository import EmployeeRepository
from backend.schemas.roster import RosterAssignmentOut, RosterOptimiseOut
from backend.services.employee_care_load import get_employee_care_load
from backend.services.risk_scoring import RiskScoringService
from backend.services.shift_matching import (
    SHIFT_PRIORITY,
    SHIFT_WEIGHTS,
    rank_shift_candidates,
    role_matches,
)


def _hours(start: datetime, end: datetime) -> float:
    return (end - start).total_seconds() / 3600


class RosterOptimisationService:
    def __init__(self, client: AsyncClient, risk_scoring_service: RiskScoringService):
        self._client = client
        self._risk_scoring_service = risk_scoring_service
        self._employee_repository = EmployeeRepository(client)
        self._shift_repository = SupabaseRepository(
            client,
            "employee_shifts",
            EmployeeShift,
            order_column="shift_start",
            parent_field="employee_id",
        )

    async def _load_shifts(
        self,
        shift_ids: list[str] | None,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> list[EmployeeShift]:
        if shift_ids:
            shifts = await asyncio.gather(
                *(self._shift_repository.get_by_id(str(sid)) for sid in shift_ids)
            )
            return [s for s in shifts if s is not None]

        all_shifts = await self._shift_repository.list_all(0, 500)
        selected = []
        for shift in all_shifts:
            if from_date and shift.shift_start < from_date:
                continue
            if to_date and shift.shift_start > to_date:
                continue
            selected.append(shift)
        return selected

    async def _employee_profile(self, employee: Employee, week_key: tuple[int, int]) -> dict:
        shifts = await self._shift_repository.list_for_parent(str(employee.id), 0, 200)
        care_load, residents = await get_employee_care_load(
            str(employee.id), self._client, self._risk_scoring_service
        )
        week_hours = sum(
            _hours(s.shift_start, s.shift_end)
            for s in shifts
            if s.shift_start.isocalendar()[:2] == week_key
        )
        return {
            "employee": employee,
            "shifts": shifts,
            "care_load": care_load,
            "residents": residents,
            "week_hours": week_hours,
        }

    async def optimise(
        self,
        shift_ids: list[str] | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        max_candidates: int = 200,
    ) -> RosterOptimiseOut:
        shifts = await self._load_shifts(shift_ids, from_date, to_date)
        shifts.sort(key=lambda s: s.shift_start)  # chronological order

        employees = await self._employee_repository.list_all(0, max_candidates)
        candidates = [e for e in employees if e.active]  # inactive employees are rejected
        result = RosterOptimiseOut(
            shifts_considered=len(shifts),
            candidates_considered=len(candidates),
            assignments=[],
            weights=SHIFT_WEIGHTS,
            priority=[field for field, _ in SHIFT_PRIORITY],
        )
        if not shifts or not candidates:
            return result

        week_key = shifts[0].shift_start.isocalendar()[:2]
        profiles = await asyncio.gather(*(self._employee_profile(e, week_key) for e in candidates))

        # Shifts already recommended in this run, per employee: (start, end).
        planned: dict[str, list[tuple[datetime, datetime]]] = {str(e.id): [] for e in candidates}

        for shift in shifts:
            rows = []
            for profile in profiles:
                employee = profile["employee"]
                busy = [
                    (s.shift_start, s.shift_end)
                    for s in profile["shifts"]
                    if str(s.id) != str(shift.id)  # the shift being filled is not its own clash
                ] + planned[str(employee.id)]
                extra_hours = sum(
                    _hours(start, end)
                    for start, end in planned[str(employee.id)]
                    if start.isocalendar()[:2] == week_key
                )
                rows.append(
                    {
                        "employee": employee,
                        # Touching shifts (one ends when the next starts) are not a clash.
                        "conflict": any(
                            start < shift.shift_end and end > shift.shift_start
                            for start, end in busy
                        ),
                        "role_match": role_matches(employee, shift),
                        "care_load": profile["care_load"],
                        "week_hours": profile["week_hours"] + extra_hours,
                    }
                )

            best = rank_shift_candidates(rows)[0]
            shift_info = dict(
                shift_id=shift.id,
                shift_start=shift.shift_start,
                shift_end=shift.shift_end,
                shift_role=shift.role,
            )
            if best["conflict"]:
                # Conflict is the first priority, so if the best still conflicts, all do.
                result.assignments.append(
                    RosterAssignmentOut(
                        **shift_info, unassigned_reason="Every candidate has a clashing shift"
                    )
                )
                continue

            employee = best["employee"]
            planned[str(employee.id)].append((shift.shift_start, shift.shift_end))
            result.assignments.append(
                RosterAssignmentOut(
                    **shift_info,
                    employee_id=employee.id,
                    employee_name=f"{employee.first_name} {employee.last_name}",
                    role_match=best["role_match"],
                    saw_score=round(best["saw_score"], 4),
                    breakdown=best["breakdown"],
                )
            )
        return result
