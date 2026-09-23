from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, model_validator


class CareVisitCreate(BaseModel):
    employee_id: UUID
    start_at: datetime
    end_at: datetime
    task: str | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def _ends_after_it_starts(self):
        if self.end_at <= self.start_at:
            raise ValueError("end_at must be after start_at")
        return self


class BookNextHourIn(BaseModel):
    """Put this carer with the resident for their next free hour on shift in the given day."""

    employee_id: UUID
    day_start: datetime | None = None
    day_end: datetime | None = None
    task: str | None = None


class CareVisitUpdate(BaseModel):
    employee_id: UUID | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    task: str | None = None
    notes: str | None = None


class CareVisitOut(BaseModel):
    id: UUID
    resident_id: UUID
    employee_id: UUID
    start_at: datetime
    end_at: datetime
    task: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
