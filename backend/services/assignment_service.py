"""Who cares for whom, answered from all three useful directions."""

import asyncio
from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException, status
from supabase import AsyncClient

from backend.models.employee import CARING_ROLES, Employee
from backend.models.employee_shift import EmployeeShift
from backend.models.resident_assignment import AssignmentType, ResidentAssignment
from backend.repositories.base import SupabaseRepository
from backend.repositories.employee_repository import EmployeeRepository
from backend.repositories.resident_assignment_repository import (
    ResidentAssignmentRepository,
)
from backend.repositories.resident_repository import ResidentRepository
from backend.schemas.resident_assignment import (
    AssignmentCreate,
    AssignmentOut,
    AssignmentUpdate,
    BulkAssignmentFailure,
    BulkAssignmentItem,
    BulkAssignmentOut,
    BulkEndOut,
    CareTeamMemberOut,
    CareTeamOut,
    CaseloadOut,
    CaseloadResidentOut,
    CoverageReportOut,
    ReassignIn,
    StaffWorkloadOut,
    UnassignedResidentOut,
    UnloadedEmployeeOut,
    WorkloadReportOut,
)
from backend.services.risk_scoring import RiskScoringService


class AssignmentService:
    def __init__(self, client: AsyncClient, risk_scoring_service: RiskScoringService):
        self._repository = ResidentAssignmentRepository(client)
        self._resident_repository = ResidentRepository(client)
        self._employee_repository = EmployeeRepository(client)
        self._shift_repository = SupabaseRepository(
            client,
            "employee_shifts",
            EmployeeShift,
            order_column="shift_start",
            parent_field="employee_id",
        )
        self._risk_scoring_service = risk_scoring_service


    async def create_assignment(
        self, resident_id: str, data: AssignmentCreate
    ) -> ResidentAssignment:
        resident, employee = await asyncio.gather(
            self._resident_repository.get_by_id(resident_id),
            self._employee_repository.get_by_id(str(data.employee_id)),
        )
        if resident is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Resident not found")
        if employee is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")
        ensure_can_care(employee)

        existing = await self._repository.list_for_resident(resident_id, active_only=True)

        if any(str(a.employee_id) == str(data.employee_id) for a in existing):
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"{employee.first_name} {employee.last_name} is already assigned to this resident",
            )

        if data.assignment_type == AssignmentType.PRIMARY:
            current_primary = next(
                (a for a in existing if a.assignment_type == AssignmentType.PRIMARY), None
            )
            if current_primary is not None:
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    "This resident already has a primary carer. Change the existing one to "
                    "Secondary first, or end that assignment.",
                )

        assignment = ResidentAssignment(
            resident_id=resident.id, **data.model_dump()
        )
        return await self._repository.create(assignment)

    async def create_many(self, items: list[BulkAssignmentItem]) -> BulkAssignmentOut:
        """Confirm several assignments at once, one at a time."""
        created: list[AssignmentOut] = []
        failed: list[BulkAssignmentFailure] = []

        for item in items:
            data = AssignmentCreate(
                employee_id=item.employee_id,
                assignment_type=item.assignment_type,
                start_date=item.start_date or date.today(),
                notes=item.notes,
            )
            try:
                assignment = await self.create_assignment(str(item.resident_id), data)
                created.append(
                    AssignmentOut.model_validate(assignment, from_attributes=True)
                )
            except HTTPException as rejection:
                failed.append(
                    BulkAssignmentFailure(
                        resident_id=item.resident_id,
                        employee_id=item.employee_id,
                        reason=str(rejection.detail),
                    )
                )

        return BulkAssignmentOut(created=created, failed=failed)

    async def list_for_resident(self, resident_id: str) -> list[ResidentAssignment]:
        if await self._resident_repository.get_by_id(resident_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Resident not found")
        return await self._repository.list_for_resident(resident_id)

    async def update_assignment(
        self, resident_id: str, assignment_id: str, data: AssignmentUpdate
    ) -> ResidentAssignment:
        existing = await self._repository.get_by_id(assignment_id)
        if existing is None or str(existing.resident_id) != resident_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Assignment not found")

        updates = data.model_dump(mode="json", exclude_unset=True)
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()

        # Ending an assignment should close it, not leave it counted as live.
        if updates.get("end_date") and "active" not in updates:
            updates["active"] = False

        updated = await self._repository.update(assignment_id, updates)
        if updated is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Assignment not found")
        return updated

    async def reassign(
        self, resident_id: str, assignment_id: str, data: ReassignIn
    ) -> ResidentAssignment:
        """Move one place on a care team from its current carer to another."""
        existing = await self._repository.get_by_id(assignment_id)
        if existing is None or str(existing.resident_id) != resident_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Assignment not found")
        if not existing.active:
            raise HTTPException(status.HTTP_409_CONFLICT, "That assignment has already ended")
        if str(existing.employee_id) == str(data.employee_id):
            raise HTTPException(
                status.HTTP_409_CONFLICT, "That carer is already in this place on the team"
            )

        employee = await self._employee_repository.get_by_id(str(data.employee_id))
        if employee is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")
        ensure_can_care(employee)

        team = await self._repository.list_for_resident(resident_id, active_only=True)
        if any(str(a.employee_id) == str(data.employee_id) for a in team):
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"{employee.first_name} {employee.last_name} is already on this resident's care team",
            )

        today = date.today()
        await self.update_assignment(
            resident_id,
            assignment_id,
            AssignmentUpdate(end_date=today, active=False),
        )
        return await self._repository.create(
            ResidentAssignment(
                resident_id=existing.resident_id,
                employee_id=data.employee_id,
                assignment_type=existing.assignment_type,
                start_date=today,
                active=True,
                notes=data.notes,
            )
        )

    async def delete_assignment(self, resident_id: str, assignment_id: str) -> None:
        existing = await self._repository.get_by_id(assignment_id)
        if existing is None or str(existing.resident_id) != resident_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Assignment not found")
        await self._repository.delete(assignment_id)

    async def end_all(self) -> BulkEndOut:
        """Close every currently active assignment, facility-wide. Kept as history, not deleted."""
        active = await self._repository.list_all(0, 5000, active_only=True)
        today = date.today().isoformat()
        results = await asyncio.gather(
            *(
                self._repository.update(
                    str(a.id),
                    {"end_date": today, "active": False},
                )
                for a in active
            ),
            return_exceptions=True,
        )
        ended = sum(1 for r in results if not isinstance(r, Exception))
        return BulkEndOut(ended_count=ended, failed_count=len(results) - ended)


    async def get_care_team(self, resident_id: str) -> CareTeamOut:
        resident = await self._resident_repository.get_by_id(resident_id)
        if resident is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Resident not found")

        assignments = await self._repository.list_for_resident(resident_id)
        if not assignments:
            return CareTeamOut(
                resident_id=resident.id,
                resident_name=f"{resident.first_name} {resident.last_name}",
                members=[],
                has_primary=False,
                on_shift_count=0,
            )

        employee_ids = [str(a.employee_id) for a in assignments if a.employee_id]
        employees, shift_lists = await asyncio.gather(
            asyncio.gather(*(self._employee_repository.get_by_id(eid) for eid in employee_ids)),
            asyncio.gather(
                *(self._shift_repository.list_for_parent(eid, 0, 100) for eid in employee_ids)
            ),
        )
        by_id = {str(e.id): e for e in employees if e is not None}
        shifts_by_id = dict(zip(employee_ids, shift_lists))

        now = datetime.now(timezone.utc)
        members: list[CareTeamMemberOut] = []
        for assignment in assignments:
            employee = by_id.get(str(assignment.employee_id))
            if employee is None:
                continue  # employee deleted; the row is orphaned
            on_now, next_start, next_end = _shift_state(shifts_by_id.get(str(employee.id), []), now)
            members.append(
                CareTeamMemberOut(
                    assignment_id=assignment.id,
                    employee_id=employee.id,
                    first_name=employee.first_name,
                    last_name=employee.last_name,
                    role=employee.role,
                    assignment_type=assignment.assignment_type,
                    start_date=assignment.start_date,
                    end_date=assignment.end_date,
                    active=assignment.active,
                    on_shift_now=on_now,
                    next_shift_start=next_start,
                    next_shift_end=next_end,
                )
            )

        # Primary first, then secondary, then relief; ended assignments last.
        order = {AssignmentType.PRIMARY: 0, AssignmentType.SECONDARY: 1, AssignmentType.RELIEF: 2}
        members.sort(key=lambda m: (not m.active, order.get(m.assignment_type, 9), m.last_name))

        return CareTeamOut(
            resident_id=resident.id,
            resident_name=f"{resident.first_name} {resident.last_name}",
            members=members,
            has_primary=any(
                m.assignment_type == AssignmentType.PRIMARY and m.active for m in members
            ),
            on_shift_count=sum(1 for m in members if m.on_shift_now and m.active),
        )


    async def get_caseload(self, employee_id: str) -> CaseloadOut:
        employee = await self._employee_repository.get_by_id(employee_id)
        if employee is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")

        assignments, shifts = await asyncio.gather(
            self._repository.list_for_employee(employee_id),
            self._shift_repository.list_for_parent(employee_id, 0, 200),
        )

        resident_ids = [str(a.resident_id) for a in assignments if a.resident_id]
        residents, scores = await asyncio.gather(
            asyncio.gather(*(self._resident_repository.get_by_id(rid) for rid in resident_ids)),
            asyncio.gather(
                *(self._risk_scoring_service.get_resident_score(rid) for rid in resident_ids)
            ),
        )
        residents_by_id = {str(r.id): r for r in residents if r is not None}
        scores_by_id = {str(s.resident_id): s for s in scores if s is not None}

        rows: list[CaseloadResidentOut] = []
        for assignment in assignments:
            resident = residents_by_id.get(str(assignment.resident_id))
            if resident is None:
                continue
            score = scores_by_id.get(str(resident.id))
            rows.append(
                CaseloadResidentOut(
                    assignment_id=assignment.id,
                    resident_id=resident.id,
                    first_name=resident.first_name,
                    last_name=resident.last_name,
                    room_number=resident.room_number,
                    assignment_type=assignment.assignment_type,
                    start_date=assignment.start_date,
                    active=assignment.active,
                    risk_score=score.score if score else None,
                    risk_band=score.band if score else None,
                )
            )

        # Riskiest residents first: that is the order a carer needs them in.
        rows.sort(key=lambda r: (not r.active, -(r.risk_score or 0)))

        week_key = datetime.now(timezone.utc).isocalendar()[:2]
        hours = sum(
            (s.shift_end - s.shift_start).total_seconds() / 3600
            for s in shifts
            if s.shift_start.isocalendar()[:2] == week_key
        )

        return CaseloadOut(
            employee_id=employee.id,
            employee_name=f"{employee.first_name} {employee.last_name}",
            residents=rows,
            primary_count=sum(
                1 for r in rows if r.active and r.assignment_type == AssignmentType.PRIMARY
            ),
            total_risk_load=sum(r.risk_score or 0 for r in rows if r.active),
            hours_this_week=round(hours, 2),
        )


    async def get_workload(self) -> WorkloadReportOut:
        """Every active staff member and how much they are carrying now."""
        employees, assignments = await asyncio.gather(
            self._employee_repository.list_all(0, 1000),
            self._repository.list_all(0, 5000, active_only=True),
        )
        active_employees = [e for e in employees if e.active]

        resident_ids = sorted({str(a.resident_id) for a in assignments if a.resident_id})
        scores = await asyncio.gather(
            *(self._risk_scoring_service.get_resident_score(rid) for rid in resident_ids)
        )
        risk_by_resident = {str(s.resident_id): s.score for s in scores if s is not None}

        by_employee: dict[str, list[ResidentAssignment]] = {}
        for assignment in assignments:
            if assignment.employee_id:
                by_employee.setdefault(str(assignment.employee_id), []).append(assignment)

        average = (
            sum(len(v) for v in by_employee.values()) / len(active_employees)
            if active_employees
            else 0.0
        )

        rows: list[StaffWorkloadOut] = []
        for employee in active_employees:
            mine = by_employee.get(str(employee.id), [])
            count = len(mine)
            if average and count > average * 1.25:
                level = "packed"
            elif count < average * 0.75:
                level = "light"
            else:
                level = "steady"
            rows.append(
                StaffWorkloadOut(
                    employee_id=employee.id,
                    first_name=employee.first_name,
                    last_name=employee.last_name,
                    role=employee.role,
                    active_residents=count,
                    primary_count=sum(
                        1 for a in mine if a.assignment_type == AssignmentType.PRIMARY
                    ),
                    total_risk_load=sum(risk_by_resident.get(str(a.resident_id), 0) for a in mine),
                    level=level,
                )
            )

        rows.sort(key=lambda r: (r.active_residents, r.total_risk_load, r.last_name))
        return WorkloadReportOut(average_residents=round(average, 2), staff=rows)


    async def get_coverage_report(self) -> CoverageReportOut:
        residents, employees, assignments = await asyncio.gather(
            self._resident_repository.list_all(0, 1000),
            self._employee_repository.list_all(0, 1000),
            self._repository.list_all(0, 5000, active_only=True),
        )

        active_residents = [r for r in residents if r.active is not False]
        active_employees = [e for e in employees if e.active and e.role in CARING_ROLES]

        carers_by_resident: dict[str, list[ResidentAssignment]] = {}
        loaded_employees: set[str] = set()
        for assignment in assignments:
            carers_by_resident.setdefault(str(assignment.resident_id), []).append(assignment)
            if assignment.employee_id:
                loaded_employees.add(str(assignment.employee_id))

        gaps = [
            r
            for r in active_residents
            if not any(
                a.assignment_type == AssignmentType.PRIMARY
                for a in carers_by_resident.get(str(r.id), [])
            )
        ]
        gap_scores = await asyncio.gather(
            *(self._risk_scoring_service.get_resident_score(str(r.id)) for r in gaps)
        )
        scores_by_id = {str(s.resident_id): s for s in gap_scores if s is not None}

        unassigned = [
            UnassignedResidentOut(
                resident_id=r.id,
                first_name=r.first_name,
                last_name=r.last_name,
                room_number=r.room_number,
                risk_score=scores_by_id[str(r.id)].score if str(r.id) in scores_by_id else None,
                risk_band=scores_by_id[str(r.id)].band if str(r.id) in scores_by_id else None,
                has_any_carer=bool(carers_by_resident.get(str(r.id))),
            )
            for r in gaps
        ]
        unassigned.sort(key=lambda r: -(r.risk_score or 0))

        staff_without_caseload = [
            UnloadedEmployeeOut(
                employee_id=e.id, first_name=e.first_name, last_name=e.last_name, role=e.role
            )
            for e in active_employees
            if str(e.id) not in loaded_employees
        ]

        with_primary = len(active_residents) - len(gaps)
        average = (
            round(len(assignments) / len(active_employees), 2) if active_employees else 0.0
        )

        return CoverageReportOut(
            total_residents=len(active_residents),
            total_active_staff=len(active_employees),
            residents_with_primary=with_primary,
            residents_without_primary=len(gaps),
            residents_with_no_carer=sum(1 for r in unassigned if not r.has_any_carer),
            average_caseload=average,
            unassigned=unassigned,
            staff_without_caseload=staff_without_caseload,
        )


def ensure_can_care(employee: Employee) -> None:
    """Managers, administrators, kitchen and laundry staff are never put on a care team."""
    if not employee.active:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            f"{employee.first_name} {employee.last_name} is not an active employee",
        )
    if employee.role not in CARING_ROLES:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            f"{employee.first_name} {employee.last_name} is {employee.role or 'without a job title'}; "
            "only care staff (" + ", ".join(sorted(CARING_ROLES)) + ") can be assigned to residents",
        )


def _shift_state(
    shifts: list[EmployeeShift], now: datetime
) -> tuple[bool, datetime | None, datetime | None]:
    """Is this person mid-shift, and when is their next one?"""
    on_now = False
    next_shift: EmployeeShift | None = None

    for shift in shifts:
        start = _as_aware(shift.shift_start)
        end = _as_aware(shift.shift_end)
        if start <= now < end:
            on_now = True
        elif start > now and (next_shift is None or start < _as_aware(next_shift.shift_start)):
            next_shift = shift

    if next_shift is None:
        return on_now, None, None
    return on_now, _as_aware(next_shift.shift_start), _as_aware(next_shift.shift_end)


def _as_aware(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


__all__ = ["AssignmentService", "timedelta"]
