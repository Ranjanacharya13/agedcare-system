from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MedicalHistoryCreate(BaseModel):
    diagnosis: str | None = None
    allergies: str | None = None
    chronic_conditions: str | None = None
    surgeries: str | None = None
    doctor_name: str | None = None
    notes: str | None = None


class MedicalHistoryUpdate(BaseModel):
    diagnosis: str | None = None
    allergies: str | None = None
    chronic_conditions: str | None = None
    surgeries: str | None = None
    doctor_name: str | None = None
    notes: str | None = None


class MedicalHistoryOut(BaseModel):
    id: UUID
    resident_id: UUID
    diagnosis: str | None = None
    allergies: str | None = None
    chronic_conditions: str | None = None
    surgeries: str | None = None
    doctor_name: str | None = None
    notes: str | None = None
    recorded_at: datetime
