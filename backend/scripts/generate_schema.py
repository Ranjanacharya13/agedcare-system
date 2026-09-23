"""Generate the Postgres schema from the Pydantic models."""

import datetime
import enum
import re
import typing
import uuid
from decimal import Decimal

from pydantic import BaseModel

from backend.models.appointment import Appointment
from backend.models.assistance import ResidentAssistance
from backend.models.audit_log import AuditLog
from backend.models.behaviour import ResidentBehaviour
from backend.models.bowel_chart import ResidentBowelChart
from backend.models.care_visit import ResidentCareVisit
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
from backend.models.resident_assignment import ResidentAssignment
from backend.models.sleep_chart import ResidentSleepChart
from backend.models.user import User

# (table, model, parent column -> parent table)
TABLES = [
    ("residents", Resident, {}),
    ("employees", Employee, {}),
    ("users", User, {"employee_id": "employees"}),
    ("audit_log", AuditLog, {}),
    ("appointments", Appointment, {"handled_by": "employees"}),
    ("complaints_feedback", ComplaintFeedback, {"resident_id": "residents", "employee_id": "employees"}),
    ("resident_medical_history", ResidentMedicalHistory, {"resident_id": "residents"}),
    (
        "resident_assignments",
        ResidentAssignment,
        {"resident_id": "residents", "employee_id": "employees"},
    ),
    (
        "resident_care_visits",
        ResidentCareVisit,
        {"resident_id": "residents", "employee_id": "employees"},
    ),
    ("resident_behaviour", ResidentBehaviour, {"resident_id": "residents", "recorded_by": "employees"}),
    ("resident_medications", ResidentMedication, {"resident_id": "residents"}),
    ("resident_bowel_chart", ResidentBowelChart, {"resident_id": "residents", "recorded_by": "employees"}),
    ("resident_sleep_chart", ResidentSleepChart, {"resident_id": "residents", "recorded_by": "employees"}),
    ("resident_fall_risk", ResidentFallRisk, {"resident_id": "residents", "assessed_by": "employees"}),
    ("resident_assistance", ResidentAssistance, {"resident_id": "residents", "updated_by": "employees"}),
    ("resident_medical_inventory", ResidentMedicalInventory, {"resident_id": "residents"}),
    ("resident_incidents", ResidentIncident, {"resident_id": "residents", "reported_by": "employees"}),
    ("employee_supervision", EmployeeSupervision, {"employee_id": "employees", "supervisor_id": "employees"}),
    ("employee_registration", EmployeeRegistration, {"employee_id": "employees"}),
    ("employee_qualifications", EmployeeQualification, {"employee_id": "employees"}),
    ("employee_performance", EmployeePerformance, {"employee_id": "employees", "reviewer_id": "employees"}),
    ("employee_leave", EmployeeLeave, {"employee_id": "employees", "approved_by": "employees"}),
    ("employee_contracts", EmployeeContract, {"employee_id": "employees"}),
    ("employee_availability", EmployeeAvailability, {"employee_id": "employees"}),
    ("employee_shifts", EmployeeShift, {"employee_id": "employees"}),
    ("employee_time_entries", EmployeeTimeEntry, {"employee_id": "employees", "shift_id": "employee_shifts"}),
    ("employee_payroll_records", EmployeePayrollRecord, {"employee_id": "employees"}),
]


def unwrap(annotation):
    """Strip Optional[...] and report nullability."""
    origin = typing.get_origin(annotation)
    if origin is typing.Union or str(origin) == "<class 'types.UnionType'>":
        args = [a for a in typing.get_args(annotation) if a is not type(None)]
        nullable = len(args) != len(typing.get_args(annotation))
        return (args[0] if args else str), nullable
    return annotation, False


def pg_type(python_type) -> str:
    if isinstance(python_type, type) and issubclass(python_type, enum.Enum):
        return "text"
    mapping = {
        uuid.UUID: "uuid",
        str: "text",
        bool: "boolean",
        int: "integer",
        float: "numeric(12, 2)",
        Decimal: "numeric(12, 2)",
        datetime.datetime: "timestamptz",
        datetime.date: "date",
        datetime.time: "time",
        dict: "jsonb",
        list: "jsonb",
    }
    if python_type in mapping:
        return mapping[python_type]
    if isinstance(python_type, type) and issubclass(python_type, BaseModel):
        return "jsonb"
    if typing.get_origin(python_type) in (dict, list):
        return "jsonb"
    return "text"


def default_for(table: str, column: str, python_type, field) -> str | None:
    if column == "id":
        return "gen_random_uuid()"
    if column in ("created_at", "updated_at"):
        return "now()"
    default = field.default
    if default is None or repr(default).startswith("PydanticUndefined"):
        return None
    if isinstance(default, enum.Enum):
        return f"'{default.value}'"
    if isinstance(default, bool):
        return "true" if default else "false"
    if isinstance(default, str):
        return f"'{default}'"
    return None


def build(table: str, model: type[BaseModel], parents: dict[str, str]) -> str:
    lines: list[str] = []
    constraints: list[str] = []
    indexes: list[str] = []

    for name, field in model.model_fields.items():
        base, nullable = unwrap(field.annotation)
        sql_type = pg_type(base)

        if name == "id":
            lines.append(f"    {name:<22} {sql_type} not null default gen_random_uuid()")
            constraints.append(f"    constraint {table}_pkey primary key (id)")
            continue

        default = default_for(table, name, base, field)
        # A field with no default and no Optional is required.
        required = not nullable and field.is_required()
        if name in ("created_at", "updated_at"):
            required = True

        parts = [f"    {name:<22} {sql_type}"]
        parts.append("not null" if required or default in ("now()",) else "null")
        if default:
            parts.append(f"default {default}")
        lines.append(" ".join(parts))

        if isinstance(base, type) and issubclass(base, enum.Enum):
            values = ", ".join(f"'{m.value}'" for m in base)
            constraints.append(
                f"    constraint {table}_{name}_check\n"
                f"        check ({name} is null or {name} = any (array[{values}]::text[]))"
            )

        if name in parents:
            target = parents[name]
            on_delete = "cascade" if name in ("resident_id", "employee_id") and table not in (
                "users", "complaints_feedback", "appointments"
            ) else "set null"
            constraints.append(
                f"    constraint {table}_{name}_fkey\n"
                f"        foreign key ({name}) references public.{target} (id) on delete {on_delete}"
            )
            indexes.append(f"create index if not exists {table}_{name}_idx on public.{table} ({name});")

    body = ",\n".join(lines + constraints)
    out = f"create table if not exists public.{table} (\n{body}\n);\n"
    if indexes:
        out += "\n".join(indexes) + "\n"
    return out


def main():
    print("-- Generated from the Pydantic models in backend/models/.")
    print("-- Regenerate rather than hand-edit: the models are the source of truth.\n")
    for table, model, parents in TABLES:
        print(f"-- {'-' * 70}")
        print(f"-- {table}")
        print(f"-- {'-' * 70}")
        print(build(table, model, parents))


if __name__ == "__main__":
    main()
