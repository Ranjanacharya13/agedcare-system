from datetime import datetime

from fastapi import APIRouter, Depends, status

from backend.api.deps import get_assignment_service, get_care_visit_service
from backend.schemas.care_visit import BookNextHourIn, CareVisitOut
from backend.schemas.resident_assignment import (
    AssignmentCreate,
    AssignmentOut,
    AssignmentUpdate,
    BulkAssignmentIn,
    BulkAssignmentOut,
    BulkEndOut,
    CareTeamOut,
    CaseloadOut,
    CoverageReportOut,
    ReassignIn,
    WorkloadReportOut,
)
from backend.services.assignment_service import AssignmentService
from backend.services.care_visit_service import CareVisitService

#: Resident-scoped CRUD: /residents/{id}/assignments
router = APIRouter()

#: Cross-cutting read-only views that do not hang off a single parent.
views_router = APIRouter()


@router.post("", response_model=AssignmentOut, status_code=status.HTTP_201_CREATED)
async def assign_employee(
    resident_id: str,
    data: AssignmentCreate,
    service: AssignmentService = Depends(get_assignment_service),
):
    """Assign a staff member to a resident as primary, secondary or relief."""
    return await service.create_assignment(resident_id, data)


@router.get("", response_model=list[AssignmentOut])
async def list_assignments(
    resident_id: str, service: AssignmentService = Depends(get_assignment_service)
):
    return await service.list_for_resident(resident_id)


@router.patch("/{assignment_id}", response_model=AssignmentOut)
async def update_assignment(
    resident_id: str,
    assignment_id: str,
    data: AssignmentUpdate,
    service: AssignmentService = Depends(get_assignment_service),
):
    return await service.update_assignment(resident_id, assignment_id, data)


@router.post("/{assignment_id}/reassign", response_model=AssignmentOut)
async def reassign_assignment(
    resident_id: str,
    assignment_id: str,
    data: ReassignIn,
    service: AssignmentService = Depends(get_assignment_service),
):
    """End this carer's place on the team and give it to someone else."""
    return await service.reassign(resident_id, assignment_id, data)


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    resident_id: str,
    assignment_id: str,
    service: AssignmentService = Depends(get_assignment_service),
):
    await service.delete_assignment(resident_id, assignment_id)


@views_router.get("/residents/{resident_id}/care-team", response_model=CareTeamOut)
async def get_care_team(
    resident_id: str, service: AssignmentService = Depends(get_assignment_service)
):
    """Who looks after this resident, and which of them is on shift now."""
    return await service.get_care_team(resident_id)


@views_router.get("/employees/{employee_id}/caseload", response_model=CaseloadOut)
async def get_caseload(
    employee_id: str, service: AssignmentService = Depends(get_assignment_service)
):
    """Which residents this employee is responsible for, riskiest first."""
    return await service.get_caseload(employee_id)


@views_router.get("/staff-workload", response_model=WorkloadReportOut)
async def get_staff_workload(
    service: AssignmentService = Depends(get_assignment_service),
):
    """How many residents each active staff member carries, and who is packed."""
    return await service.get_workload()


@views_router.get("/coverage", response_model=CoverageReportOut)
async def get_coverage_report(
    service: AssignmentService = Depends(get_assignment_service),
):
    return await service.get_coverage_report()


@views_router.post("/coverage/assignments", response_model=BulkAssignmentOut)
async def create_assignments_in_bulk(
    payload: BulkAssignmentIn,
    service: AssignmentService = Depends(get_assignment_service),
):
    """Confirm a set of assignments in one action."""
    return await service.create_many(payload.assignments)


@views_router.post("/coverage/assignments/end-all", response_model=BulkEndOut)
async def end_all_assignments(
    service: AssignmentService = Depends(get_assignment_service),
):
    """End every currently active assignment, facility-wide. Kept as history, not deleted."""
    return await service.end_all()


@views_router.get("/care-schedule", response_model=list[CareVisitOut])
async def get_care_schedule(
    start: datetime,
    end: datetime,
    service: CareVisitService = Depends(get_care_visit_service),
):
    """Every care visit overlapping [start, end), earliest first. The browser sends its local day."""
    return await service.list_between(start, end)


@views_router.post(
    "/residents/{resident_id}/care-visits/next-free-hour", response_model=CareVisitOut | None
)
async def book_next_free_hour(
    resident_id: str,
    payload: BookNextHourIn,
    service: CareVisitService = Depends(get_care_visit_service),
):
    """Book the carer's next free hour on shift today; null if they have none left."""
    return await service.book_next_free_hour(
        resident_id,
        str(payload.employee_id),
        payload.day_start,
        payload.day_end,
        payload.task,
    )
