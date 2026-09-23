from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, Field


class ResidentCareVisit(BaseModel):
    """One block of the daily care schedule: this carer is with this resident from start to end."""

    id: UUID | None = None
    resident_id: UUID | None = None
    employee_id: UUID
    start_at: datetime
    end_at: datetime
    task: str | None = None
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
