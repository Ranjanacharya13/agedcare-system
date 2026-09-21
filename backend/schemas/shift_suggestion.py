from uuid import UUID

from pydantic import BaseModel

from backend.schemas.decision import CriterionOut


class ShiftSuggestionOut(BaseModel):
    employee_id: UUID
    first_name: str
    last_name: str
    role: str | None = None
    current_week_hours: float
    conflict: bool
    care_load_score: float
    residents_cared_for_recently: int
    #: SAW score, 0..1, higher is better. Ranking is lexicographic, see shift_matching.py.
    role_match: bool = True
    saw_score: float = 0.0
    rank: int = 0
    breakdown: list[CriterionOut] = []
