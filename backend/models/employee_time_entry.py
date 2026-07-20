from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, Field


class EmployeeTimeEntry(BaseModel):
    id: UUID | None = None
    employee_id: UUID | None = None
    shift_id: UUID | None = None
    clock_in: datetime
    clock_out: datetime | None = None
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
