from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from backend.models.employee import EmployeeRole
from backend.models.resident_assignment import AssignmentType


class AssignmentCreate(BaseModel):
    employee_id: UUID
    assignment_type: AssignmentType = AssignmentType.SECONDARY
    start_date: date | None = None
    end_date: date | None = None
    active: bool = True
    notes: str | None = None


class AssignmentUpdate(BaseModel):
    employee_id: UUID | None = None
    assignment_type: AssignmentType | None = None
    start_date: date | None = None
    end_date: date | None = None
    active: bool | None = None
    notes: str | None = None


class AssignmentOut(BaseModel):
    id: UUID
    resident_id: UUID
    employee_id: UUID | None = None
    assignment_type: AssignmentType
    start_date: date | None = None
    end_date: date | None = None
    active: bool
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class ReassignIn(BaseModel):
    """Hand one resident's place on a care team to a different carer."""

    employee_id: UUID
    notes: str | None = None


class BulkAssignmentItem(BaseModel):
    """One confirmed line of a proposed allocation."""

    resident_id: UUID
    employee_id: UUID
    assignment_type: AssignmentType = AssignmentType.PRIMARY
    start_date: date | None = None
    notes: str | None = None


class BulkAssignmentIn(BaseModel):
    assignments: list[BulkAssignmentItem]


class BulkAssignmentFailure(BaseModel):
    resident_id: UUID
    employee_id: UUID
    reason: str


class BulkAssignmentOut(BaseModel):
    """Deliberately not all-or-nothing."""

    created: list[AssignmentOut]
    failed: list[BulkAssignmentFailure]


class CareTeamMemberOut(BaseModel):
    assignment_id: UUID
    employee_id: UUID
    first_name: str
    last_name: str
    role: EmployeeRole | None = None
    assignment_type: AssignmentType
    start_date: date | None = None
    end_date: date | None = None
    active: bool
    #: True when this carer is inside a rostered shift right now.
    on_shift_now: bool = False
    #: Their next rostered shift, if any is scheduled.
    next_shift_start: datetime | None = None
    next_shift_end: datetime | None = None


class CareTeamOut(BaseModel):
    resident_id: UUID
    resident_name: str
    members: list[CareTeamMemberOut]
    has_primary: bool
    on_shift_count: int


class CaseloadResidentOut(BaseModel):
    assignment_id: UUID
    resident_id: UUID
    first_name: str
    last_name: str
    room_number: str | None = None
    assignment_type: AssignmentType
    start_date: date | None = None
    active: bool
    risk_score: int | None = None
    risk_band: str | None = None


class CaseloadOut(BaseModel):
    employee_id: UUID
    employee_name: str
    residents: list[CaseloadResidentOut]
    primary_count: int
    total_risk_load: int
    hours_this_week: float


class StaffWorkloadOut(BaseModel):
    employee_id: UUID
    first_name: str
    last_name: str
    role: EmployeeRole | None = None
    active_residents: int
    primary_count: int
    total_risk_load: int
    level: str


class WorkloadReportOut(BaseModel):
    average_residents: float
    staff: list[StaffWorkloadOut]


class UnassignedResidentOut(BaseModel):
    resident_id: UUID
    first_name: str
    last_name: str
    room_number: str | None = None
    risk_score: int | None = None
    risk_band: str | None = None
    #: Distinguishes "nobody at all" from "covered, but no named key worker".
    has_any_carer: bool


class UnloadedEmployeeOut(BaseModel):
    employee_id: UUID
    first_name: str
    last_name: str
    role: EmployeeRole | None = None


class CoverageReportOut(BaseModel):
    total_residents: int
    total_active_staff: int
    residents_with_primary: int
    residents_without_primary: int
    residents_with_no_carer: int
    average_caseload: float
    unassigned: list[UnassignedResidentOut]
    staff_without_caseload: list[UnloadedEmployeeOut]
