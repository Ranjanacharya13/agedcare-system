from datetime import date
from uuid import UUID

from pydantic import BaseModel


class QualificationCreate(BaseModel):
    qualification_name: str | None = None
    institution: str | None = None
    completion_date: date | None = None
    expiry_date: date | None = None


class QualificationUpdate(BaseModel):
    qualification_name: str | None = None
    institution: str | None = None
    completion_date: date | None = None
    expiry_date: date | None = None


class QualificationOut(BaseModel):
    id: UUID
    employee_id: UUID
    qualification_name: str | None = None
    institution: str | None = None
    completion_date: date | None = None
    expiry_date: date | None = None
