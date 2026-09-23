from uuid import UUID

from pydantic import BaseModel


class RiskScoreBreakdownItem(BaseModel):
    value: str
    points: int
    weight: float = 0.0
    normalised: float = 0.0


class RiskScoreOut(BaseModel):
    resident_id: UUID
    first_name: str
    last_name: str
    score: int
    band: str
    breakdown: dict[str, RiskScoreBreakdownItem]


class CriterionWeightOut(BaseModel):
    criterion: str
    weight: float
    percentage: float


class RiskWeightModelOut(BaseModel):
    method: str
    weights: dict[str, float]
    criteria: list[CriterionWeightOut]
