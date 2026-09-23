"""The hour-by-hour care schedule: which carer is with which resident, when."""

import asyncio
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from pydantic import BaseModel
from supabase import AsyncClient

from backend.models.care_visit import ResidentCareVisit
from backend.models.employee_shift import EmployeeShift, ShiftStatus
from backend.repositories.base import SupabaseRepository
from backend.repositories.care_visit_repository import CareVisitRepository
from backend.repositories.employee_repository import EmployeeRepository
from backend.repositories.resident_repository import ResidentRepository
from backend.schemas.care_visit import CareVisitCreate
from backend.services.assignment_service import ensure_can_care
from backend.services.base import ParentScopedService


VISIT_LENGTH = timedelta(hours=1)
NOT_WORKING = frozenset({ShiftStatus.CANCELLED, ShiftStatus.NO_SHOW})


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


def day_window(
    start: datetime | None = None, end: datetime | None = None
) -> tuple[datetime, datetime]:
    """The day being planned. The browser sends its local midnight-to-midnight; default is the UTC day."""
    if start and end:
        return _aware(start), _aware(end)
    midnight = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight, midnight + timedelta(days=1)


def next_free_hour(
    shifts: list[EmployeeShift], busy: list[ResidentCareVisit], not_before: datetime
) -> tuple[datetime, datetime] | None:
    """First one-hour slot inside a working shift, on the hour, clear of every busy visit."""
    for shift in shifts:
        if shift.status in NOT_WORKING:
            continue
        shift_start, shift_end = _aware(shift.shift_start), _aware(shift.shift_end)
        slot = shift_start
        if not_before > shift_start:  # shift already running: start on the next whole hour
            slot = not_before.replace(minute=0, second=0, microsecond=0)
            if slot < not_before:
                slot += timedelta(hours=1)
        while slot + VISIT_LENGTH <= shift_end:
            clash = next(
                (v for v in busy if _aware(v.start_at) < slot + VISIT_LENGTH and _aware(v.end_at) > slot),
                None,
            )
            if clash is None:
                return slot, slot + VISIT_LENGTH
            slot = max(slot + VISIT_LENGTH, _aware(clash.end_at))
    return None


class CareVisitService(ParentScopedService[ResidentCareVisit]):
    def __init__(self, client: AsyncClient):
        super().__init__(
            CareVisitRepository(client),
            ResidentRepository(client),
            ResidentCareVisit,
            "resident_id",
            "Care visit not found",
            parent_not_found_message="Resident not found",
        )
        self._employee_repository = EmployeeRepository(client)
        self._shift_repository = SupabaseRepository(
            client, "employee_shifts", EmployeeShift, parent_field="employee_id"
        )

    async def _check(
        self, employee_id, start: datetime, end: datetime, ignore_id: str | None = None
    ) -> None:
        """Same carer rules as care teams, plus: nobody is in two places at once."""
        start, end = _aware(start), _aware(end)
        if end <= start:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "End must be after start")

        employee = await self._employee_repository.get_by_id(str(employee_id))
        if employee is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")
        ensure_can_care(employee)

        clashes = [
            v
            for v in await self._repository.list_between(start, end, str(employee_id))
            if str(v.id) != ignore_id
        ]
        if clashes:
            first = clashes[0]
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"{employee.first_name} {employee.last_name} already has a visit "
                f"{first.start_at:%Y-%m-%d %H:%M}-{first.end_at:%H:%M} UTC that overlaps this time",
            )

    async def create_record(self, parent_id: str, data: BaseModel) -> ResidentCareVisit:
        await self._check(data.employee_id, data.start_at, data.end_at)
        return await super().create_record(parent_id, data)

    async def update_record(
        self, parent_id: str, record_id: str, data: BaseModel
    ) -> ResidentCareVisit:
        current = await self.get_record(parent_id, record_id)
        merged = current.model_copy(update=data.model_dump(exclude_unset=True))
        await self._check(merged.employee_id, merged.start_at, merged.end_at, ignore_id=record_id)
        return await super().update_record(parent_id, record_id, data)

    async def list_between(self, start: datetime, end: datetime) -> list[ResidentCareVisit]:
        return await self._repository.list_between(_aware(start), _aware(end))

    async def book_next_free_hour(
        self,
        resident_id: str,
        employee_id: str,
        day_start: datetime | None = None,
        day_end: datetime | None = None,
        task: str | None = None,
    ) -> ResidentCareVisit | None:
        """Put this carer with this resident for their next free hour on shift today.

        None when they are not rostered for the rest of the day or every hour is taken.
        """
        await self._ensure_parent_exists(resident_id)
        day_start, day_end = day_window(day_start, day_end)
        not_before = max(day_start, datetime.now(timezone.utc))
        shifts, busy = await asyncio.gather(
            self._shift_repository.list_overlapping(
                "shift_start", "shift_end", not_before, day_end, employee_id=employee_id
            ),
            self._repository.list_between(not_before, day_end, employee_id),
        )
        slot = next_free_hour(shifts, busy, not_before)
        if slot is None:
            return None
        return await self.create_record(
            resident_id,
            CareVisitCreate(employee_id=employee_id, start_at=slot[0], end_at=slot[1], task=task),
        )
