from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class ComplaintStatus(StrEnum):
    OPEN = "Open"
    INVESTIGATING = "Investigating"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class ComplaintFeedback(BaseModel):
    id: UUID | None = None
    resident_id: UUID | None = None
    employee_id: UUID | None = None
    category: str
    description: str
    submitted_by_name: str
    submitted_by_relationship: str | None = None
    submitted_by_contact: str | None = None
    is_anonymous: bool = False
    status: ComplaintStatus = ComplaintStatus.OPEN
    assigned_to: UUID | None = None
    resolution_notes: str | None = None
    resolved_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
