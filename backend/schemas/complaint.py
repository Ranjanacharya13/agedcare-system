from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from backend.models.complaint import ComplaintStatus


class ComplaintCreate(BaseModel):
    resident_id: UUID | None = None
    employee_id: UUID | None = None
    category: str
    description: str
    submitted_by_name: str
    submitted_by_relationship: str | None = None
    submitted_by_contact: str | None = None
    is_anonymous: bool = False
    status: ComplaintStatus | None = ComplaintStatus.OPEN
    assigned_to: UUID | None = None


class ComplaintUpdate(BaseModel):
    resident_id: UUID | None = None
    employee_id: UUID | None = None
    category: str | None = None
    description: str | None = None
    submitted_by_name: str | None = None
    submitted_by_relationship: str | None = None
    submitted_by_contact: str | None = None
    is_anonymous: bool | None = None
    status: ComplaintStatus | None = None
    assigned_to: UUID | None = None
    resolution_notes: str | None = None
    resolved_at: datetime | None = None


class ComplaintOut(BaseModel):
    id: UUID
    resident_id: UUID | None = None
    employee_id: UUID | None = None
    category: str
    description: str
    submitted_by_name: str
    submitted_by_relationship: str | None = None
    submitted_by_contact: str | None = None
    is_anonymous: bool
    status: ComplaintStatus
    assigned_to: UUID | None = None
    resolution_notes: str | None = None
    resolved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
