from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TimeEntryCreate(BaseModel):
    shift_id: UUID | None = None
    clock_in: datetime
    clock_out: datetime | None = None
    notes: str | None = None


class TimeEntryUpdate(BaseModel):
    shift_id: UUID | None = None
    clock_in: datetime | None = None
    clock_out: datetime | None = None
    notes: str | None = None


class TimeEntryOut(BaseModel):
    id: UUID
    employee_id: UUID
    shift_id: UUID | None = None
    clock_in: datetime
    clock_out: datetime | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
