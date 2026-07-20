from datetime import date, datetime, time, timezone
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class AppointmentStatus(StrEnum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"


class Appointment(BaseModel):
    id: UUID | None = None
    full_name: str
    email: str
    phone: str | None = None
    appointment_type: str
    preferred_date: date | None = None
    preferred_time: time | None = None
    message: str | None = None
    status: AppointmentStatus = AppointmentStatus.PENDING
    scheduled_at: datetime | None = None
    handled_by: UUID | None = None
    admin_notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
