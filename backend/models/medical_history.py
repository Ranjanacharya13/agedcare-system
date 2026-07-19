from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, Field


class ResidentMedicalHistory(BaseModel):
    id: UUID | None = None
    resident_id: UUID | None = None
    diagnosis: str | None = None
    allergies: str | None = None
    chronic_conditions: str | None = None
    surgeries: str | None = None
    doctor_name: str | None = None
    notes: str | None = None
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
