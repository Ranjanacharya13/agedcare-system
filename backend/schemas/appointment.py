from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from backend.models.appointment import AppointmentStatus


class AppointmentCreate(BaseModel):
    """Publicly submittable fields only."""

    full_name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=40)
    appointment_type: str = Field(min_length=1, max_length=120)
    preferred_date: date | None = None
    preferred_time: time | None = None
    message: str | None = Field(default=None, max_length=4000)


class AppointmentUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=200)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=40)
    appointment_type: str | None = Field(default=None, min_length=1, max_length=120)
    preferred_date: date | None = None
    preferred_time: time | None = None
    message: str | None = None
    status: AppointmentStatus | None = None
    scheduled_at: datetime | None = None
    handled_by: UUID | None = None
    admin_notes: str | None = None


class AppointmentOut(BaseModel):
    id: UUID
    full_name: str
    email: str
    phone: str | None = None
    appointment_type: str
    preferred_date: date | None = None
    preferred_time: time | None = None
    message: str | None = None
    status: AppointmentStatus
    scheduled_at: datetime | None = None
    handled_by: UUID | None = None
    admin_notes: str | None = None
    created_at: datetime
    updated_at: datetime
