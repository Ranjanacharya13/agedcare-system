from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class EmployeePerformance(BaseModel):
    id: UUID | None = None
    employee_id: UUID | None = None
    reviewer: UUID | None = None
    review_date: date | None = None
    overall_rating: int | None = Field(default=None, ge=1, le=5)
    strengths: str | None = None
    improvements: str | None = None
    goals: str | None = None
    next_review: date | None = None
