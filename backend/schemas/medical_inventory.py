from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class MedicalInventoryCreate(BaseModel):
    item_name: str | None = None
    quantity: int | None = 0
    unit: str | None = None
    expiry_date: date | None = None
    notes: str | None = None
    added_by: UUID | None = None


class MedicalInventoryUpdate(BaseModel):
    item_name: str | None = None
    quantity: int | None = None
    unit: str | None = None
    expiry_date: date | None = None
    notes: str | None = None
    added_by: UUID | None = None


class MedicalInventoryOut(BaseModel):
    id: UUID
    resident_id: UUID
    item_name: str | None = None
    quantity: int | None = None
    unit: str | None = None
    expiry_date: date | None = None
    notes: str | None = None
    added_by: UUID | None = None
    created_at: datetime
