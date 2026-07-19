from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BowelChartCreate(BaseModel):
    bowel_type: str | None = None
    consistency: str | None = None
    notes: str | None = None
    recorded_by: UUID | None = None


class BowelChartUpdate(BaseModel):
    bowel_type: str | None = None
    consistency: str | None = None
    notes: str | None = None
    recorded_by: UUID | None = None


class BowelChartOut(BaseModel):
    id: UUID
    resident_id: UUID
    recorded_at: datetime
    bowel_type: str | None = None
    consistency: str | None = None
    notes: str | None = None
    recorded_by: UUID | None = None
