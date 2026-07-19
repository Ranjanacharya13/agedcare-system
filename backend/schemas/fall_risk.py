from datetime import date
from uuid import UUID

from pydantic import BaseModel

from backend.models.fall_risk import RiskLevel


class FallRiskCreate(BaseModel):
    risk_level: RiskLevel | None = None
    assessment_date: date | None = None
    assessed_by: UUID | None = None
    interventions: str | None = None
    notes: str | None = None


class FallRiskUpdate(BaseModel):
    risk_level: RiskLevel | None = None
    assessment_date: date | None = None
    assessed_by: UUID | None = None
    interventions: str | None = None
    notes: str | None = None


class FallRiskOut(BaseModel):
    id: UUID
    resident_id: UUID
    risk_level: RiskLevel | None = None
    assessment_date: date | None = None
    assessed_by: UUID | None = None
    interventions: str | None = None
    notes: str | None = None
