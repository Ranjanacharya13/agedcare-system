from datetime import date
from uuid import UUID

from pydantic import BaseModel


class ContractCreate(BaseModel):
    contract_type: str | None = None
    contracted_hours: float | None = None
    hourly_rate: float | None = None
    start_date: date | None = None
    end_date: date | None = None
    annual_leave_hours: float | None = None
    sick_leave_hours: float | None = None
    notes: str | None = None


class ContractUpdate(BaseModel):
    contract_type: str | None = None
    contracted_hours: float | None = None
    hourly_rate: float | None = None
    start_date: date | None = None
    end_date: date | None = None
    annual_leave_hours: float | None = None
    sick_leave_hours: float | None = None
    notes: str | None = None


class ContractOut(BaseModel):
    id: UUID
    employee_id: UUID
    contract_type: str | None = None
    contracted_hours: float | None = None
    hourly_rate: float | None = None
    start_date: date | None = None
    end_date: date | None = None
    annual_leave_hours: float | None = None
    sick_leave_hours: float | None = None
    notes: str | None = None
