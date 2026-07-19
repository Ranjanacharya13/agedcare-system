from datetime import date
from uuid import UUID

from pydantic import BaseModel


class SupervisionCreate(BaseModel):
    supervisor: UUID | None = None
    supervision_date: date | None = None
    discussion: str | None = None
    action_items: str | None = None
    follow_up_date: date | None = None


class SupervisionUpdate(BaseModel):
    supervisor: UUID | None = None
    supervision_date: date | None = None
    discussion: str | None = None
    action_items: str | None = None
    follow_up_date: date | None = None


class SupervisionOut(BaseModel):
    id: UUID
    employee_id: UUID
    supervisor: UUID | None = None
    supervision_date: date | None = None
    discussion: str | None = None
    action_items: str | None = None
    follow_up_date: date | None = None
