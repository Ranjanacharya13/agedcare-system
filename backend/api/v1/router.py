from fastapi import APIRouter, Depends

from backend.api import deps
from backend.api.auth_deps import require_permission
from backend.api.v1.endpoints import (
    appointments,
    assignments,
    carer_suggestions,
    audit_log,
    auth,
    complaints,
    employees,
    health,
    public_appointments,
    residents,
    risk_scores,
    roster,
    shift_suggestions,
)
from backend.api.v1.parent_scoped_router import build_parent_scoped_routers
from backend.schemas.assistance import AssistanceCreate, AssistanceOut, AssistanceUpdate
from backend.schemas.behaviour import BehaviourCreate, BehaviourOut, BehaviourUpdate
from backend.schemas.care_visit import CareVisitCreate, CareVisitOut, CareVisitUpdate
from backend.schemas.bowel_chart import BowelChartCreate, BowelChartOut, BowelChartUpdate
from backend.schemas.employee_availability import (
    AvailabilityCreate,
    AvailabilityOut,
    AvailabilityUpdate,
)
from backend.schemas.employee_contract import ContractCreate, ContractOut, ContractUpdate
from backend.schemas.employee_leave import LeaveCreate, LeaveOut, LeaveUpdate
from backend.schemas.employee_payroll_record import PayrollCreate, PayrollOut, PayrollUpdate
from backend.schemas.employee_performance import (
    PerformanceCreate,
    PerformanceOut,
    PerformanceUpdate,
)
from backend.schemas.employee_qualification import (
    QualificationCreate,
    QualificationOut,
    QualificationUpdate,
)
from backend.schemas.employee_registration import (
    RegistrationCreate,
    RegistrationOut,
    RegistrationUpdate,
)
from backend.schemas.employee_shift import ShiftCreate, ShiftOut, ShiftUpdate
from backend.schemas.employee_supervision import (
    SupervisionCreate,
    SupervisionOut,
    SupervisionUpdate,
)
from backend.schemas.employee_time_entry import TimeEntryCreate, TimeEntryOut, TimeEntryUpdate
from backend.schemas.fall_risk import FallRiskCreate, FallRiskOut, FallRiskUpdate
from backend.schemas.incident import IncidentCreate, IncidentOut, IncidentUpdate
from backend.schemas.medical_history import (
    MedicalHistoryCreate,
    MedicalHistoryOut,
    MedicalHistoryUpdate,
)
from backend.schemas.medical_inventory import (
    MedicalInventoryCreate,
    MedicalInventoryOut,
    MedicalInventoryUpdate,
)
from backend.schemas.medication import MedicationCreate, MedicationOut, MedicationUpdate
from backend.schemas.sleep_chart import SleepChartCreate, SleepChartOut, SleepChartUpdate

api_router = APIRouter()


def _guard(group: str) -> list:
    """Every router below is mounted with exactly one of these."""
    return [Depends(require_permission(group))]


api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(
    public_appointments.router, prefix="/appointments", tags=["appointments-public"]
)

api_router.include_router(
    auth.users_router, prefix="/users", tags=["users"]
)
api_router.include_router(
    audit_log.router, prefix="/audit-log", tags=["audit"], dependencies=_guard("audit")
)
api_router.include_router(
    residents.router, prefix="/residents", tags=["residents"], dependencies=_guard("residents")
)
api_router.include_router(
    assignments.router,
    prefix="/residents/{resident_id}/assignments",
    tags=["assignments"],
    dependencies=_guard("assignments"),
)
api_router.include_router(
    assignments.views_router, tags=["assignments"], dependencies=_guard("assignments")
)
api_router.include_router(
    carer_suggestions.router, tags=["assignments"], dependencies=_guard("assignments")
)
api_router.include_router(
    employees.router, prefix="/employees", tags=["employees"], dependencies=_guard("employees")
)
api_router.include_router(
    complaints.router, prefix="/complaints", tags=["complaints"], dependencies=_guard("complaints")
)
api_router.include_router(
    appointments.router,
    prefix="/appointments",
    tags=["appointments"],
    dependencies=_guard("appointments"),
)
api_router.include_router(
    risk_scores.router, tags=["risk-scores"], dependencies=_guard("analytics")
)
api_router.include_router(
    shift_suggestions.router, tags=["shift-suggestions"], dependencies=_guard("analytics")
)
api_router.include_router(
    roster.weights_router, tags=["risk-weights"], dependencies=_guard("analytics")
)
api_router.include_router(
    roster.router, tags=["roster"], dependencies=_guard("roster_planning")
)

_RESIDENT_RESOURCES = [
    (
        "behaviour",
        BehaviourCreate,
        BehaviourUpdate,
        BehaviourOut,
        deps.get_behaviour_service,
        "resident_charts",
    ),
    (
        "medications",
        MedicationCreate,
        MedicationUpdate,
        MedicationOut,
        deps.get_medication_service,
        "resident_clinical",
    ),
    (
        "bowel-chart",
        BowelChartCreate,
        BowelChartUpdate,
        BowelChartOut,
        deps.get_bowel_chart_service,
        "resident_charts",
    ),
    (
        "sleep-chart",
        SleepChartCreate,
        SleepChartUpdate,
        SleepChartOut,
        deps.get_sleep_chart_service,
        "resident_charts",
    ),
    (
        "fall-risk",
        FallRiskCreate,
        FallRiskUpdate,
        FallRiskOut,
        deps.get_fall_risk_service,
        "resident_clinical",
    ),
    (
        "assistance",
        AssistanceCreate,
        AssistanceUpdate,
        AssistanceOut,
        deps.get_assistance_service,
        "resident_charts",
    ),
    (
        "medical-history",
        MedicalHistoryCreate,
        MedicalHistoryUpdate,
        MedicalHistoryOut,
        deps.get_medical_history_service,
        "resident_clinical",
    ),
    (
        "medical-inventory",
        MedicalInventoryCreate,
        MedicalInventoryUpdate,
        MedicalInventoryOut,
        deps.get_medical_inventory_service,
        "resident_clinical",
    ),
    (
        "incidents",
        IncidentCreate,
        IncidentUpdate,
        IncidentOut,
        deps.get_incident_service,
        "resident_charts",
    ),
    (
        "care-visits",
        CareVisitCreate,
        CareVisitUpdate,
        CareVisitOut,
        deps.get_care_visit_service,
        "assignments",
    ),
]

_EMPLOYEE_RESOURCES = [
    (
        "supervision",
        SupervisionCreate,
        SupervisionUpdate,
        SupervisionOut,
        deps.get_supervision_service,
        "employee_hr",
    ),
    (
        "registration",
        RegistrationCreate,
        RegistrationUpdate,
        RegistrationOut,
        deps.get_registration_service,
        "employee_hr",
    ),
    (
        "qualifications",
        QualificationCreate,
        QualificationUpdate,
        QualificationOut,
        deps.get_qualification_service,
        "employee_hr",
    ),
    (
        "performance",
        PerformanceCreate,
        PerformanceUpdate,
        PerformanceOut,
        deps.get_performance_service,
        "employee_hr",
    ),
    ("leave", LeaveCreate, LeaveUpdate, LeaveOut, deps.get_leave_service, "employee_hr"),
    (
        "contracts",
        ContractCreate,
        ContractUpdate,
        ContractOut,
        deps.get_contract_service,
        "employee_hr",
    ),
    (
        "availability",
        AvailabilityCreate,
        AvailabilityUpdate,
        AvailabilityOut,
        deps.get_availability_service,
        "employee_roster",
    ),
    ("shifts", ShiftCreate, ShiftUpdate, ShiftOut, deps.get_shift_service, "employee_roster"),
    (
        "time-entries",
        TimeEntryCreate,
        TimeEntryUpdate,
        TimeEntryOut,
        deps.get_time_entry_service,
        "employee_roster",
    ),
    (
        "payroll",
        PayrollCreate,
        PayrollUpdate,
        PayrollOut,
        deps.get_payroll_service,
        "employee_hr",
    ),
]

for _slug, _create, _update, _out, _get_service, _group in _RESIDENT_RESOURCES:
    _router, _all_router = build_parent_scoped_routers(
        parent_param="resident_id",
        create_schema=_create,
        update_schema=_update,
        out_schema=_out,
        get_service=_get_service,
    )
    api_router.include_router(
        _all_router, prefix=f"/{_slug}", tags=[_slug], dependencies=_guard(_group)
    )
    api_router.include_router(
        _router,
        prefix=f"/residents/{{resident_id}}/{_slug}",
        tags=[_slug],
        dependencies=_guard(_group),
    )

for _slug, _create, _update, _out, _get_service, _group in _EMPLOYEE_RESOURCES:
    _router, _all_router = build_parent_scoped_routers(
        parent_param="employee_id",
        create_schema=_create,
        update_schema=_update,
        out_schema=_out,
        get_service=_get_service,
    )
    api_router.include_router(
        _all_router, prefix=f"/{_slug}", tags=[_slug], dependencies=_guard(_group)
    )
    api_router.include_router(
        _router,
        prefix=f"/employees/{{employee_id}}/{_slug}",
        tags=[_slug],
        dependencies=_guard(_group),
    )
