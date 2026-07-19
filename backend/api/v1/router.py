from fastapi import APIRouter

from backend.api import deps
from backend.api.v1.endpoints import employees, health, medical_history, residents
from backend.api.v1.parent_scoped_router import build_parent_scoped_routers
from backend.schemas.assistance import AssistanceCreate, AssistanceOut, AssistanceUpdate
from backend.schemas.behaviour import BehaviourCreate, BehaviourOut, BehaviourUpdate
from backend.schemas.bowel_chart import BowelChartCreate, BowelChartOut, BowelChartUpdate
from backend.schemas.employee_availability import (
    AvailabilityCreate,
    AvailabilityOut,
    AvailabilityUpdate,
)
from backend.schemas.employee_contract import ContractCreate, ContractOut, ContractUpdate
from backend.schemas.employee_leave import LeaveCreate, LeaveOut, LeaveUpdate
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
from backend.schemas.employee_supervision import (
    SupervisionCreate,
    SupervisionOut,
    SupervisionUpdate,
)
from backend.schemas.fall_risk import FallRiskCreate, FallRiskOut, FallRiskUpdate
from backend.schemas.medical_inventory import (
    MedicalInventoryCreate,
    MedicalInventoryOut,
    MedicalInventoryUpdate,
)
from backend.schemas.medication import MedicationCreate, MedicationOut, MedicationUpdate
from backend.schemas.sleep_chart import SleepChartCreate, SleepChartOut, SleepChartUpdate

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(residents.router, prefix="/residents", tags=["residents"])
api_router.include_router(employees.router, prefix="/employees", tags=["employees"])
api_router.include_router(
    medical_history.all_router, prefix="/medical-history", tags=["medical-history"]
)
api_router.include_router(
    medical_history.router,
    prefix="/residents/{resident_id}/medical-history",
    tags=["medical-history"],
)

_RESIDENT_RESOURCES = [
    ("behaviour", BehaviourCreate, BehaviourUpdate, BehaviourOut, deps.get_behaviour_service),
    ("medications", MedicationCreate, MedicationUpdate, MedicationOut, deps.get_medication_service),
    (
        "bowel-chart",
        BowelChartCreate,
        BowelChartUpdate,
        BowelChartOut,
        deps.get_bowel_chart_service,
    ),
    (
        "sleep-chart",
        SleepChartCreate,
        SleepChartUpdate,
        SleepChartOut,
        deps.get_sleep_chart_service,
    ),
    ("fall-risk", FallRiskCreate, FallRiskUpdate, FallRiskOut, deps.get_fall_risk_service),
    ("assistance", AssistanceCreate, AssistanceUpdate, AssistanceOut, deps.get_assistance_service),
    (
        "medical-inventory",
        MedicalInventoryCreate,
        MedicalInventoryUpdate,
        MedicalInventoryOut,
        deps.get_medical_inventory_service,
    ),
]

_EMPLOYEE_RESOURCES = [
    (
        "supervision",
        SupervisionCreate,
        SupervisionUpdate,
        SupervisionOut,
        deps.get_supervision_service,
    ),
    (
        "registration",
        RegistrationCreate,
        RegistrationUpdate,
        RegistrationOut,
        deps.get_registration_service,
    ),
    (
        "qualifications",
        QualificationCreate,
        QualificationUpdate,
        QualificationOut,
        deps.get_qualification_service,
    ),
    (
        "performance",
        PerformanceCreate,
        PerformanceUpdate,
        PerformanceOut,
        deps.get_performance_service,
    ),
    ("leave", LeaveCreate, LeaveUpdate, LeaveOut, deps.get_leave_service),
    ("contracts", ContractCreate, ContractUpdate, ContractOut, deps.get_contract_service),
    (
        "availability",
        AvailabilityCreate,
        AvailabilityUpdate,
        AvailabilityOut,
        deps.get_availability_service,
    ),
]

for _slug, _create, _update, _out, _get_service in _RESIDENT_RESOURCES:
    _router, _all_router = build_parent_scoped_routers(
        parent_param="resident_id",
        create_schema=_create,
        update_schema=_update,
        out_schema=_out,
        get_service=_get_service,
    )
    api_router.include_router(_all_router, prefix=f"/{_slug}", tags=[_slug])
    api_router.include_router(
        _router, prefix=f"/residents/{{resident_id}}/{_slug}", tags=[_slug]
    )

for _slug, _create, _update, _out, _get_service in _EMPLOYEE_RESOURCES:
    _router, _all_router = build_parent_scoped_routers(
        parent_param="employee_id",
        create_schema=_create,
        update_schema=_update,
        out_schema=_out,
        get_service=_get_service,
    )
    api_router.include_router(_all_router, prefix=f"/{_slug}", tags=[_slug])
    api_router.include_router(
        _router, prefix=f"/employees/{{employee_id}}/{_slug}", tags=[_slug]
    )
