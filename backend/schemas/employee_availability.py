from datetime import time
from uuid import UUID

from pydantic import BaseModel


class AvailabilityCreate(BaseModel):
    weekday: str | None = None
    start_time: time | None = None
    end_time: time | None = None
    available: bool | None = True


class AvailabilityUpdate(BaseModel):
    weekday: str | None = None
    start_time: time | None = None
    end_time: time | None = None
    available: bool | None = None


class AvailabilityOut(BaseModel):
    id: UUID
    employee_id: UUID
    weekday: str | None = None
    start_time: time | None = None
    end_time: time | None = None
    available: bool | None = None
