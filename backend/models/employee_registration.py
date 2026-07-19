from datetime import date
from uuid import UUID

from pydantic import BaseModel


class EmployeeRegistration(BaseModel):
    id: UUID | None = None
    employee_id: UUID | None = None
    registration_type: str | None = None
    registration_number: str | None = None
    issuing_authority: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    verified: bool | None = False
