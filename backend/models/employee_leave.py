from datetime import date
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class LeaveStatus(StrEnum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    CANCELLED = "Cancelled"


class EmployeeLeave(BaseModel):
    id: UUID | None = None
    employee_id: UUID | None = None
    leave_type: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: LeaveStatus | None = None
    approved_by: UUID | None = None
    notes: str | None = None
