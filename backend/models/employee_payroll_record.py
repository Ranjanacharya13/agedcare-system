from datetime import date, datetime, timezone
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class PayrollStatus(StrEnum):
    DRAFT = "Draft"
    FINALIZED = "Finalized"
    PAID = "Paid"


class EmployeePayrollRecord(BaseModel):
    # Totals/gross/net are recorded, not computed. Aggregating employee_time_entries
    # (hours) x employee_contracts.hourly_rate into these fields is a future enhancement.
    id: UUID | None = None
    employee_id: UUID | None = None
    pay_period_start: date
    pay_period_end: date
    total_hours: float | None = None
    hourly_rate: float | None = None
    gross_pay: float | None = None
    deductions: float | None = 0
    net_pay: float | None = None
    status: PayrollStatus = PayrollStatus.DRAFT
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
