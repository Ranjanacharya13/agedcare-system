from datetime import date
from uuid import UUID

from pydantic import BaseModel

from backend.models.employee_leave import LeaveStatus


class LeaveCreate(BaseModel):
    leave_type: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: LeaveStatus | None = None
    approved_by: UUID | None = None
    notes: str | None = None


class LeaveUpdate(BaseModel):
    leave_type: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: LeaveStatus | None = None
    approved_by: UUID | None = None
    notes: str | None = None


class LeaveOut(BaseModel):
    id: UUID
    employee_id: UUID
    leave_type: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: LeaveStatus | None = None
    approved_by: UUID | None = None
    notes: str | None = None
