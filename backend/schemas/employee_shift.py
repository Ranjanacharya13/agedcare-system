from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, model_validator

from backend.models.employee_shift import ShiftStatus


class ShiftCreate(BaseModel):
    shift_start: datetime
    shift_end: datetime
    role: str | None = None
    location: str | None = None
    status: ShiftStatus | None = ShiftStatus.SCHEDULED
    notes: str | None = None

    @model_validator(mode="after")
    def _ends_after_it_starts(self):
        if self.shift_end <= self.shift_start:
            raise ValueError("shift_end must be after shift_start")
        return self


class ShiftUpdate(BaseModel):
    shift_start: datetime | None = None
    shift_end: datetime | None = None
    role: str | None = None
    location: str | None = None
    status: ShiftStatus | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def _ends_after_it_starts(self):
        # ponytail: only catches the case where both are edited together;
        # a lone shift_start/shift_end edit still relies on the DB check constraint.
        if self.shift_start is not None and self.shift_end is not None and self.shift_end <= self.shift_start:
            raise ValueError("shift_end must be after shift_start")
        return self


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
