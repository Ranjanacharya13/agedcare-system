from datetime import date, datetime, timezone
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class EmployeeRole(StrEnum):
    CARE_PARTNER = "Care Partner"
    CLINICAL_COORDINATOR = "Clinical Coordinator"
    REGISTERED_NURSE = "Registered Nurse"
    KITCHEN_STAFF = "Kitchen Staff"
    LAUNDRY_STAFF = "Laundry Staff"
    ADMINISTRATOR = "Administrator"
    MANAGER = "Manager"


class EmploymentStatus(StrEnum):
    FULL_TIME = "Full-Time"
    PART_TIME = "Part-Time"
    CASUAL = "Casual"
    AGENCY = "Agency"


class Employee(BaseModel):
    id: UUID | None = None
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
