from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from backend.models.employee_payroll_record import PayrollStatus


class PayrollCreate(BaseModel):
    pay_period_start: date
    pay_period_end: date
    total_hours: float | None = None
    hourly_rate: float | None = None
    gross_pay: float | None = None
    deductions: float | None = 0
    net_pay: float | None = None
    status: PayrollStatus | None = PayrollStatus.DRAFT
    notes: str | None = None


class PayrollUpdate(BaseModel):
    pay_period_start: date | None = None
    pay_period_end: date | None = None
    total_hours: float | None = None
    hourly_rate: float | None = None
    gross_pay: float | None = None
    deductions: float | None = None
    net_pay: float | None = None
    status: PayrollStatus | None = None
    notes: str | None = None


class PayrollOut(BaseModel):
    id: UUID
    employee_id: UUID
    pay_period_start: date
    pay_period_end: date
    total_hours: float | None = None
    hourly_rate: float | None = None
    gross_pay: float | None = None
    deductions: float | None = None
    net_pay: float | None = None
    status: PayrollStatus
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
