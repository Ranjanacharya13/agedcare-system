from datetime import date, datetime, timezone
from enum import StrEnum

from pydantic import Field

from backend.models.base import MongoBaseModel


class CognitiveStatus(StrEnum):
    COGNITIVE = "cognitive"
    IN_COGNITIVE = "in_cognitive"


class ResidentClassification(StrEnum):
    COGNITIVE = "cognitive"
    IN_COGNITIVE = "in_cognitive"
    DISABLED = "disabled"


class Resident(MongoBaseModel):
    full_name: str
    date_of_birth: date
    room_number: str
    care_level: str
    classification: ResidentClassification
    disability_cognitive_status: CognitiveStatus | None = None
    medical_notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
