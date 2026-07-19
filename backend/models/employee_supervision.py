from datetime import date
from uuid import UUID

from pydantic import BaseModel


class EmployeeSupervision(BaseModel):
    id: UUID | None = None
    employee_id: UUID | None = None
    supervisor: UUID | None = None
    supervision_date: date | None = None
    discussion: str | None = None
    action_items: str | None = None
    follow_up_date: date | None = None
