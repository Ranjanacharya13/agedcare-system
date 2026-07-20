from uuid import UUID

from pydantic import BaseModel


class RiskScoreBreakdownItem(BaseModel):
    value: str
    points: int


class RiskScoreOut(BaseModel):
    resident_id: UUID
    first_name: str
    last_name: str
    score: int
    band: str
    breakdown: dict[str, RiskScoreBreakdownItem]
