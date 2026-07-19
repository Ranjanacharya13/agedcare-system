from datetime import date, time
from uuid import UUID

from pydantic import BaseModel


class ResidentSleepChart(BaseModel):
    id: UUID | None = None
    resident_id: UUID | None = None
    sleep_date: date | None = None
    sleep_start: time | None = None
    wake_time: time | None = None
    total_hours: float | None = None
    disturbances: str | None = None
    recorded_by: UUID | None = None
