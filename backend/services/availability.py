"""Whether a staff member said they can work a given day.

Availability is entered per weekday (free text, e.g. "Monday") with an
`available` flag. Absence of any record for that weekday means no
information was ever entered, not "unavailable" - so it does not exclude
anyone. Only an explicit `available = False` for that weekday does.
"""

from __future__ import annotations

from datetime import datetime

from backend.models.employee_availability import EmployeeAvailability


def is_available(records: list[EmployeeAvailability], when: datetime) -> bool:
    weekday = when.strftime("%A").lower()
    matching = [r for r in records if r.weekday and r.weekday.strip().lower() == weekday]
    if not matching:
        return True
    return any(r.available for r in matching)


def group_by_employee(
    records: list[EmployeeAvailability],
) -> dict[str, list[EmployeeAvailability]]:
    by_employee: dict[str, list[EmployeeAvailability]] = {}
    for record in records:
        if record.employee_id:
            by_employee.setdefault(str(record.employee_id), []).append(record)
    return by_employee
