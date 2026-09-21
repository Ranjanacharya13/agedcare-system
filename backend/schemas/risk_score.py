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


class AHPCriterionOut(BaseModel):
    criterion: str
    weight: float
    percentage: float


class RiskWeightModelOut(BaseModel):

    method: str
    criteria: list[AHPCriterionOut]
    comparison_matrix: list[list[float]]
    lambda_max: float
    consistency_index: float
    consistency_ratio: float
    consistency_threshold: float
    is_consistent: bool
    verdict: str
