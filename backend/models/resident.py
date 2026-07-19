from datetime import date, datetime, timezone
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CognitiveStatus(StrEnum):
    COGNITIVE = "Cognitive"
    NON_COGNITIVE = "Non-Cognitive"
    DISABLED_COGNITIVE = "Disabled-Cognitive"
    DISABLED_NON_COGNITIVE = "Disabled-Non-Cognitive"


class EmergencyContact(BaseModel):
    name: str
    relationship: str | None = None
    phone: str | None = None
    email: str | None = None


class Resident(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID | None = None
    first_name: str
    last_name: str
    dob: date | None = None
    gender: str | None = None
    cognitive_status: CognitiveStatus | None = None
    room_number: str | None = None
    admission_date: date | None = None
    emergency_contact: EmergencyContact | None = None
    active: bool | None = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
