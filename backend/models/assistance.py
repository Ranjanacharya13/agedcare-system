from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class AssistanceLevel(StrEnum):
    INDEPENDENT = "Independent"
    SINGLE_ASSIST = "Single Assist"
    DOUBLE_ASSIST = "Double Assist"


class ResidentAssistance(BaseModel):
    id: UUID | None = None
    resident_id: UUID | None = None
    assistance_level: AssistanceLevel | None = None
    mobility: str | None = None
    transfer_notes: str | None = None
    updated_by: UUID | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
