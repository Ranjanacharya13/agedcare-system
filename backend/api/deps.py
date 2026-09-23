from typing import Callable

from pydantic import BaseModel
from supabase import AsyncClient

from backend.db.supabase_client import get_supabase
from backend.models.appointment import Appointment
from backend.models.assistance import ResidentAssistance
from backend.models.behaviour import ResidentBehaviour
from backend.models.bowel_chart import ResidentBowelChart
from backend.models.complaint import ComplaintFeedback
from backend.models.employee import Employee
from backend.models.employee_availability import EmployeeAvailability
from backend.models.employee_contract import EmployeeContract
from backend.models.employee_leave import EmployeeLeave
from backend.models.employee_payroll_record import EmployeePayrollRecord
from backend.models.employee_performance import EmployeePerformance
from backend.models.employee_qualification import EmployeeQualification
from backend.models.employee_registration import EmployeeRegistration
from backend.models.employee_shift import EmployeeShift
from backend.models.employee_supervision import EmployeeSupervision
from backend.models.employee_time_entry import EmployeeTimeEntry
from backend.models.fall_risk import ResidentFallRisk
from backend.models.incident import ResidentIncident
from backend.models.medical_history import ResidentMedicalHistory
from backend.models.medical_inventory import ResidentMedicalInventory
from backend.models.medication import ResidentMedication
from backend.models.resident import Resident
from backend.models.sleep_chart import ResidentSleepChart
from backend.repositories.appointment_repository import AppointmentRepository
from backend.repositories.audit_repository import AuditRepository
from backend.repositories.base import SupabaseRepository
from backend.repositories.complaint_repository import ComplaintRepository
from backend.repositories.employee_repository import EmployeeRepository
from backend.repositories.resident_repository import ResidentRepository
from backend.services.base import CrudService, ParentScopedService
from backend.services.assignment_service import AssignmentService
from backend.services.care_visit_service import CareVisitService
from backend.services.carer_matching import CarerMatchingService
from backend.services.risk_scoring import RiskScoringService
from backend.services.roster_optimisation import RosterOptimisationService
from backend.services.shift_matching import ShiftMatchingService


def get_db() -> AsyncClient:
    return get_supabase()


def get_audit_repository() -> AuditRepository:
    return AuditRepository(get_db())


def get_resident_service() -> CrudService:
    return CrudService(ResidentRepository(get_db()), Resident, "Resident")


def get_employee_service() -> CrudService:
    return CrudService(EmployeeRepository(get_db()), Employee, "Employee")


def get_complaint_service() -> CrudService:
    return CrudService(ComplaintRepository(get_db()), ComplaintFeedback, "Complaint")


def get_appointment_service() -> CrudService:
    return CrudService(AppointmentRepository(get_db()), Appointment, "Appointment")


def get_risk_scoring_service() -> RiskScoringService:
    return RiskScoringService(get_db())


def get_assignment_service() -> AssignmentService:
    client = get_db()
    return AssignmentService(client, RiskScoringService(client))


def get_care_visit_service() -> CareVisitService:
    return CareVisitService(get_db())


def get_carer_matching_service() -> CarerMatchingService:
    client = get_db()
    return CarerMatchingService(client, RiskScoringService(client))


def get_roster_optimisation_service() -> RosterOptimisationService:
    client = get_db()
    return RosterOptimisationService(client, RiskScoringService(client))


def get_shift_matching_service() -> ShiftMatchingService:
    client = get_db()
    return ShiftMatchingService(client, RiskScoringService(client))


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


get_behaviour_service = _make_scoped_service_getter(
    "resident_behaviour", ResidentBehaviour, "recorded_at", "Behaviour record not found"
)
get_medical_history_service = _make_scoped_service_getter(
    "resident_medical_history",
    ResidentMedicalHistory,
    "recorded_at",
    "Medical history record not found",
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
get_incident_service = _make_scoped_service_getter(
    "resident_incidents", ResidentIncident, "occurred_at", "Incident record not found"
)


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
get_shift_service = _make_scoped_service_getter(
    "employee_shifts",
    EmployeeShift,
    "shift_start",
    "Shift record not found",
    parent_field="employee_id",
    parent_repository_factory=EmployeeRepository,
    parent_not_found_message="Employee not found",
)
get_time_entry_service = _make_scoped_service_getter(
    "employee_time_entries",
    EmployeeTimeEntry,
    "clock_in",
    "Time entry not found",
    parent_field="employee_id",
    parent_repository_factory=EmployeeRepository,
    parent_not_found_message="Employee not found",
)
get_payroll_service = _make_scoped_service_getter(
    "employee_payroll_records",
    EmployeePayrollRecord,
    "pay_period_start",
    "Payroll record not found",
    parent_field="employee_id",
    parent_repository_factory=EmployeeRepository,
    parent_not_found_message="Employee not found",
)
