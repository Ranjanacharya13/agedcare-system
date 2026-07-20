from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class ShiftStatus(StrEnum):
    SCHEDULED = "Scheduled"
    CONFIRMED = "Confirmed"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    NO_SHOW = "No-Show"


class EmployeeShift(BaseModel):
    id: UUID | None = None
    employee_id: UUID | None = None
    shift_start: datetime
    shift_end: datetime
    role: str | None = None
    location: str | None = None
    status: ShiftStatus = ShiftStatus.SCHEDULED
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
