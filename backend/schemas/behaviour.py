from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BehaviourCreate(BaseModel):
    behaviour: str | None = None
    trigger: str | None = None
    intervention: str | None = None
    outcome: str | None = None
    recorded_by: UUID | None = None


class BehaviourUpdate(BaseModel):
    behaviour: str | None = None
    trigger: str | None = None
    intervention: str | None = None
    outcome: str | None = None
    recorded_by: UUID | None = None


class BehaviourOut(BaseModel):
    id: UUID
    resident_id: UUID
    behaviour: str | None = None
    trigger: str | None = None
    intervention: str | None = None
    outcome: str | None = None
    recorded_by: UUID | None = None
    recorded_at: datetime
