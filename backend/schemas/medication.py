from datetime import date
from uuid import UUID

from pydantic import BaseModel


class MedicationCreate(BaseModel):
    medication_name: str | None = None
    dosage: str | None = None
    frequency: str | None = None
    route: str | None = None
    prescribed_by: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    active: bool | None = True
    notes: str | None = None


class MedicationUpdate(BaseModel):
    medication_name: str | None = None
    dosage: str | None = None
    frequency: str | None = None
    route: str | None = None
    prescribed_by: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    active: bool | None = None
    notes: str | None = None


class MedicationOut(BaseModel):
    id: UUID
    resident_id: UUID
    medication_name: str | None = None
    dosage: str | None = None
    frequency: str | None = None
    route: str | None = None
    prescribed_by: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    active: bool | None = None
    notes: str | None = None
