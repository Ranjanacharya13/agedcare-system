from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from backend.models.employee import EmployeeRole, EmploymentStatus


class EmployeeCreate(BaseModel):
    employee_number: str | None = None
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    role: EmployeeRole | None = None
    employment_status: EmploymentStatus | None = None
    hire_date: date | None = None
    termination_date: date | None = None
    active: bool | None = True


class EmployeeUpdate(BaseModel):
    employee_number: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    role: EmployeeRole | None = None
    employment_status: EmploymentStatus | None = None
    hire_date: date | None = None
    termination_date: date | None = None
    active: bool | None = None


class EmployeeOut(BaseModel):
    id: UUID
    employee_number: str | None = None
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    role: EmployeeRole | None = None
    employment_status: EmploymentStatus | None = None
    hire_date: date | None = None
    termination_date: date | None = None
    active: bool | None = None
    created_at: datetime
    updated_at: datetime
