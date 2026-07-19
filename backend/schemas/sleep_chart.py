from datetime import date, time
from uuid import UUID

from pydantic import BaseModel


class SleepChartCreate(BaseModel):
    sleep_date: date | None = None
    sleep_start: time | None = None
    wake_time: time | None = None
    total_hours: float | None = None
    disturbances: str | None = None
    recorded_by: UUID | None = None


class SleepChartUpdate(BaseModel):
    sleep_date: date | None = None
    sleep_start: time | None = None
    wake_time: time | None = None
    total_hours: float | None = None
    disturbances: str | None = None
    recorded_by: UUID | None = None


class SleepChartOut(BaseModel):
    id: UUID
    resident_id: UUID
    sleep_date: date | None = None
    sleep_start: time | None = None
    wake_time: time | None = None
    total_hours: float | None = None
    disturbances: str | None = None
    recorded_by: UUID | None = None
