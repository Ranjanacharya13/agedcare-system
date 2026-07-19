from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, Field


class ResidentBehaviour(BaseModel):
    id: UUID | None = None
    resident_id: UUID | None = None
    behaviour: str | None = None
    trigger: str | None = None
    intervention: str | None = None
    outcome: str | None = None
    recorded_by: UUID | None = None
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
