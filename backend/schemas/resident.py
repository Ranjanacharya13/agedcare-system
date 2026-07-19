from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from backend.models.resident import CognitiveStatus, EmergencyContact


class ResidentCreate(BaseModel):
    first_name: str
    last_name: str
    dob: date | None = None
    gender: str | None = None
    cognitive_status: CognitiveStatus | None = None
    room_number: str | None = None
    admission_date: date | None = None
    emergency_contact: EmergencyContact | None = None
    active: bool | None = True


class ResidentUpdate(BaseModel):
    resident_code: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    dob: date | None = None
    gender: str | None = None
    cognitive_status: CognitiveStatus | None = None
    room_number: str | None = None
    admission_date: date | None = None
    emergency_contact: EmergencyContact | None = None
    active: bool | None = None


class ResidentOut(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    dob: date | None = None
    gender: str | None = None
    cognitive_status: CognitiveStatus | None = None
    room_number: str | None = None
    admission_date: date | None = None
    emergency_contact: EmergencyContact | None = None
    active: bool | None = None
    created_at: datetime
    updated_at: datetime
