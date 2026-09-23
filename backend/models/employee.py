from datetime import date, datetime, timezone
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class EmployeeRole(StrEnum):
    CARE_PLANNER = "Care Planner"
    CARE_COORDINATOR = "Care Coordinator"
    REGISTERED_NURSE = "Registered Nurse"
    KITCHEN_STAFF = "Kitchen Staff"
    LAUNDRY_STAFF = "Laundry Staff"
    ADMINISTRATOR = "Administrator"
    MANAGER = "Manager"


#: Roles that deliver hands-on care. Only these may join a care team or be scheduled
#: with a resident; managers, administrators, kitchen and laundry staff never are.
CARING_ROLES = frozenset(
    {EmployeeRole.REGISTERED_NURSE, EmployeeRole.CARE_PLANNER, EmployeeRole.CARE_COORDINATOR}
)


class EmploymentStatus(StrEnum):
    FULL_TIME = "Full-Time"
    PART_TIME = "Part-Time"
    CASUAL = "Casual"
    AGENCY = "Agency"


class Employee(BaseModel):
    id: UUID | None = None
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    role: EmployeeRole | None = None
    employment_status: EmploymentStatus | None = None
    hire_date: date | None = None
    termination_date: date | None = None
    active: bool | None = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
