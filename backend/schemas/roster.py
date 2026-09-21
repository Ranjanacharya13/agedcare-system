from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from backend.schemas.decision import CriterionOut


class RosterOptimiseRequest(BaseModel):
    """Which shifts to fill."""

    shift_ids: list[UUID] | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None
    max_candidates: int = Field(default=200, ge=1, le=1000)


class RosterAssignmentOut(BaseModel):
    shift_id: UUID
    shift_start: datetime
    shift_end: datetime
    shift_role: str | None = None
    employee_id: UUID | None = None
    employee_name: str | None = None
    role_match: bool | None = None
    #: SAW score of the recommended employee, 0..1, higher is better.
    saw_score: float | None = None
    breakdown: list[CriterionOut] = []
    unassigned_reason: str | None = None


class RosterOptimiseOut(BaseModel):
    """SAW-based roster recommendation (not a globally optimal roster)."""

    shifts_considered: int
    candidates_considered: int
    assignments: list[RosterAssignmentOut]
    weights: dict[str, float]
    #: Lexicographic priority, most important first.
    priority: list[str]
