from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel

from backend.models.appointment import AppointmentStatus


class AppointmentCreate(BaseModel):
    full_name: str
    email: str
    phone: str | None = None
    appointment_type: str
    preferred_date: date | None = None
    preferred_time: time | None = None
    message: str | None = None


class AppointmentUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    appointment_type: str | None = None
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
