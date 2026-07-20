from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from backend.models.employee_shift import ShiftStatus


class ShiftCreate(BaseModel):
    shift_start: datetime
    shift_end: datetime
    role: str | None = None
    location: str | None = None
    status: ShiftStatus | None = ShiftStatus.SCHEDULED
    notes: str | None = None


class ShiftUpdate(BaseModel):
    shift_start: datetime | None = None
    shift_end: datetime | None = None
    role: str | None = None
    location: str | None = None
    status: ShiftStatus | None = None
    notes: str | None = None


class ShiftOut(BaseModel):
    id: UUID
    employee_id: UUID
    shift_start: datetime
    shift_end: datetime
    role: str | None = None
    location: str | None = None
    status: ShiftStatus
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
