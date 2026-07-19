from typing import Callable

from pydantic import BaseModel
from supabase import AsyncClient

from backend.db.supabase_client import get_supabase
from backend.models.assistance import ResidentAssistance
from backend.models.behaviour import ResidentBehaviour
from backend.models.bowel_chart import ResidentBowelChart
from backend.models.employee_availability import EmployeeAvailability
from backend.models.employee_contract import EmployeeContract
from backend.models.employee_leave import EmployeeLeave
from backend.models.employee_performance import EmployeePerformance
from backend.models.employee_qualification import EmployeeQualification
from backend.models.employee_registration import EmployeeRegistration
from backend.models.employee_supervision import EmployeeSupervision
from backend.models.fall_risk import ResidentFallRisk
from backend.models.medical_inventory import ResidentMedicalInventory
from backend.models.medication import ResidentMedication
from backend.models.sleep_chart import ResidentSleepChart
from backend.repositories.base import SupabaseRepository
from backend.repositories.employee_repository import EmployeeRepository
from backend.repositories.medical_history_repository import MedicalHistoryRepository
from backend.repositories.resident_repository import ResidentRepository
from backend.services.base import ParentScopedService
from backend.services.employee_service import EmployeeService
from backend.services.medical_history_service import MedicalHistoryService
from backend.services.resident_service import ResidentService


def get_db() -> AsyncClient:
    return get_supabase()


def get_resident_service() -> ResidentService:
    repository = ResidentRepository(get_db())
    return ResidentService(repository)


def get_employee_service() -> EmployeeService:
    repository = EmployeeRepository(get_db())
    return EmployeeService(repository)


def get_medical_history_service() -> MedicalHistoryService:
    repository = MedicalHistoryRepository(get_db())
    resident_repository = ResidentRepository(get_db())
    return MedicalHistoryService(repository, resident_repository)


def _make_scoped_service_getter(
    table_name: str,
    model: type[BaseModel],
    order_column: str | None,
    not_found_message: str,
    *,
    parent_field: str = "resident_id",
    parent_repository_factory: Callable[[AsyncClient], object] = ResidentRepository,
    parent_not_found_message: str = "Resident not found",
) -> Callable[[], ParentScopedService]:
    def _get_service() -> ParentScopedService:
        client = get_db()
        repository = SupabaseRepository(
            client, table_name, model, order_column=order_column, parent_field=parent_field
        )
        parent_repository = parent_repository_factory(client)
        return ParentScopedService(
            repository,
            parent_repository,
            model,
            parent_field,
            not_found_message,
            parent_not_found_message=parent_not_found_message,
        )

    return _get_service


# --- resident-scoped charts ---

get_behaviour_service = _make_scoped_service_getter(
    "resident_behaviour", ResidentBehaviour, "recorded_at", "Behaviour record not found"
)
get_medication_service = _make_scoped_service_getter(
    "resident_medications", ResidentMedication, None, "Medication not found"
)
get_bowel_chart_service = _make_scoped_service_getter(
    "resident_bowel_chart", ResidentBowelChart, "recorded_at", "Bowel chart entry not found"
)
get_sleep_chart_service = _make_scoped_service_getter(
    "resident_sleep_chart", ResidentSleepChart, "sleep_date", "Sleep chart entry not found"
)
get_fall_risk_service = _make_scoped_service_getter(
    "resident_fall_risk", ResidentFallRisk, "assessment_date", "Fall risk assessment not found"
)
get_assistance_service = _make_scoped_service_getter(
    "resident_assistance", ResidentAssistance, "updated_at", "Assistance record not found"
)
get_medical_inventory_service = _make_scoped_service_getter(
    "resident_medical_inventory",
    ResidentMedicalInventory,
    "created_at",
    "Medical inventory item not found",
)

# --- employee-scoped records ---

get_supervision_service = _make_scoped_service_getter(
    "employee_supervision",
    EmployeeSupervision,
    "supervision_date",
    "Supervision record not found",
    parent_field="employee_id",
    parent_repository_factory=EmployeeRepository,
    parent_not_found_message="Employee not found",
)
get_registration_service = _make_scoped_service_getter(
    "employee_registration",
    EmployeeRegistration,
    "issue_date",
    "Registration record not found",
    parent_field="employee_id",
    parent_repository_factory=EmployeeRepository,
    parent_not_found_message="Employee not found",
)
get_qualification_service = _make_scoped_service_getter(
    "employee_qualifications",
    EmployeeQualification,
    "completion_date",
    "Qualification record not found",
    parent_field="employee_id",
    parent_repository_factory=EmployeeRepository,
    parent_not_found_message="Employee not found",
)
get_performance_service = _make_scoped_service_getter(
    "employee_performance",
    EmployeePerformance,
    "review_date",
    "Performance record not found",
    parent_field="employee_id",
    parent_repository_factory=EmployeeRepository,
    parent_not_found_message="Employee not found",
)
get_leave_service = _make_scoped_service_getter(
    "employee_leave",
    EmployeeLeave,
    "start_date",
    "Leave record not found",
    parent_field="employee_id",
    parent_repository_factory=EmployeeRepository,
    parent_not_found_message="Employee not found",
)
get_contract_service = _make_scoped_service_getter(
    "employee_contracts",
    EmployeeContract,
    "start_date",
    "Contract record not found",
    parent_field="employee_id",
    parent_repository_factory=EmployeeRepository,
    parent_not_found_message="Employee not found",
)
get_availability_service = _make_scoped_service_getter(
    "employee_availability",
    EmployeeAvailability,
    None,
    "Availability record not found",
    parent_field="employee_id",
    parent_repository_factory=EmployeeRepository,
    parent_not_found_message="Employee not found",
)
