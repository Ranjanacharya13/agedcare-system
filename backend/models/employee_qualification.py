from datetime import date
from uuid import UUID

from pydantic import BaseModel


class EmployeeQualification(BaseModel):
    id: UUID | None = None
    employee_id: UUID | None = None
    qualification_name: str | None = None
    institution: str | None = None
    completion_date: date | None = None
    expiry_date: date | None = None
