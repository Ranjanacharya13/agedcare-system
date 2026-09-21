from uuid import UUID

from pydantic import BaseModel

from backend.models.employee import EmployeeRole
from backend.schemas.decision import CriterionOut


class CarerCandidateOut(BaseModel):
    """One ranked option while assigning a resident, with the reasoning."""

    employee_id: UUID
    first_name: str
    last_name: str
    role: EmployeeRole | None = None
    current_caseload: int
    current_risk_load: int
    role_suitable: bool = True
    #: SAW score, 0..1, higher is better.
    saw_score: float
    rank: int
    breakdown: list[CriterionOut] = []
    reason: str


class CarerSuggestionOut(BaseModel):
    """One row of a proposed allocation: this resident, that carer."""

    resident_id: UUID
    first_name: str
    last_name: str
    room_number: str | None = None
    risk_score: int | None = None
    risk_band: str | None = None
    employee_id: UUID | None = None
    employee_name: str | None = None
    employee_role: EmployeeRole | None = None
    saw_score: float | None = None
    reason: str
    alternatives: list[CarerCandidateOut] = []


class SuggestAssignmentsOut(BaseModel):
    """A whole proposed allocation. Nothing is written until a person confirms."""

    residents_needing_a_carer: int
    candidates_considered: int
    suggestions: list[CarerSuggestionOut]
    unmatched: int = 0
