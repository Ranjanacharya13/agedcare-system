from datetime import time
from uuid import UUID

from pydantic import BaseModel


class EmployeeAvailability(BaseModel):
    id: UUID | None = None
    employee_id: UUID | None = None
    weekday: str | None = None
    start_time: time | None = None
    end_time: time | None = None
    available: bool | None = True
