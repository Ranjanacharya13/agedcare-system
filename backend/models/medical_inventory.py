from datetime import date, datetime, timezone
from uuid import UUID

from pydantic import BaseModel, Field


class ResidentMedicalInventory(BaseModel):
    id: UUID | None = None
    resident_id: UUID | None = None
    item_name: str | None = None
    quantity: int | None = 0
    unit: str | None = None
    expiry_date: date | None = None
    notes: str | None = None
    added_by: UUID | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
