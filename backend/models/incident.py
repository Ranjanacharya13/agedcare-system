from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class IncidentSeverity(StrEnum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class IncidentStatus(StrEnum):
    OPEN = "Open"
    UNDER_REVIEW = "Under Review"
    REPORTED = "Reported"
    CLOSED = "Closed"


class ResidentIncident(BaseModel):
    id: UUID | None = None
    resident_id: UUID | None = None
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
    status: IncidentStatus = IncidentStatus.OPEN
    outcome: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
