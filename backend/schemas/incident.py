from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from backend.models.incident import IncidentSeverity, IncidentStatus


class IncidentCreate(BaseModel):
    incident_type: str
    severity: IncidentSeverity
    description: str
    occurred_at: datetime
    location: str | None = None
    reported_by: UUID | None = None
    witnesses: str | None = None
    immediate_action: str | None = None
    is_sirs_reportable: bool = False
    sirs_notified_at: datetime | None = None
    sirs_reference_number: str | None = None
    status: IncidentStatus | None = IncidentStatus.OPEN
    outcome: str | None = None


class IncidentUpdate(BaseModel):
    incident_type: str | None = None
    severity: IncidentSeverity | None = None
    description: str | None = None
    occurred_at: datetime | None = None
    location: str | None = None
    reported_by: UUID | None = None
    witnesses: str | None = None
    immediate_action: str | None = None
    is_sirs_reportable: bool | None = None
    sirs_notified_at: datetime | None = None
    sirs_reference_number: str | None = None
    status: IncidentStatus | None = None
    outcome: str | None = None


class IncidentOut(BaseModel):
    id: UUID
    resident_id: UUID
    incident_type: str
    severity: IncidentSeverity
    description: str
    occurred_at: datetime
    location: str | None = None
    reported_by: UUID | None = None
    witnesses: str | None = None
    immediate_action: str | None = None
    is_sirs_reportable: bool
    sirs_notified_at: datetime | None = None
    sirs_reference_number: str | None = None
    status: IncidentStatus
    outcome: str | None = None
    created_at: datetime
    updated_at: datetime
