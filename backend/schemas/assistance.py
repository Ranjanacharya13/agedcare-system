from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from backend.models.assistance import AssistanceLevel


class AssistanceCreate(BaseModel):
    assistance_level: AssistanceLevel | None = None
    mobility: str | None = None
    transfer_notes: str | None = None
    updated_by: UUID | None = None


class AssistanceUpdate(BaseModel):
    assistance_level: AssistanceLevel | None = None
    mobility: str | None = None
    transfer_notes: str | None = None
    updated_by: UUID | None = None


class AssistanceOut(BaseModel):
    id: UUID
    resident_id: UUID
    assistance_level: AssistanceLevel | None = None
    mobility: str | None = None
    transfer_notes: str | None = None
    updated_by: UUID | None = None
    updated_at: datetime
