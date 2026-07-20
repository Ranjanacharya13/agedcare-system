from uuid import UUID

from pydantic import BaseModel


class ShiftSuggestionOut(BaseModel):
    employee_id: UUID
    first_name: str
    last_name: str
    role: str | None = None
    current_week_hours: float
    conflict: bool
    care_load_score: float
    residents_cared_for_recently: int
