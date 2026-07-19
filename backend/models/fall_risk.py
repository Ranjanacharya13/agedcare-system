from datetime import date
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class RiskLevel(StrEnum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class ResidentFallRisk(BaseModel):
    id: UUID | None = None
    resident_id: UUID | None = None
    risk_level: RiskLevel | None = None
    assessment_date: date | None = None
    assessed_by: UUID | None = None
    interventions: str | None = None
    notes: str | None = None
