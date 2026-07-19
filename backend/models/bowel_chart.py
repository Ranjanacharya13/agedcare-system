from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, Field


class ResidentBowelChart(BaseModel):
    id: UUID | None = None
    resident_id: UUID | None = None
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    bowel_type: str | None = None
    consistency: str | None = None
    notes: str | None = None
    recorded_by: UUID | None = None
