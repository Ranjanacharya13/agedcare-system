from datetime import date
from uuid import UUID

from pydantic import BaseModel


class RegistrationCreate(BaseModel):
    registration_type: str | None = None
    registration_number: str | None = None
    issuing_authority: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    verified: bool | None = False


class RegistrationUpdate(BaseModel):
    registration_type: str | None = None
    registration_number: str | None = None
    issuing_authority: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    verified: bool | None = None


class RegistrationOut(BaseModel):
    id: UUID
    employee_id: UUID
    registration_type: str | None = None
    registration_number: str | None = None
    issuing_authority: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    verified: bool | None = None
