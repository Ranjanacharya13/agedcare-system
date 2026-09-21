"""Care assignments — the link between employees and residents."""

from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi import HTTPException

from backend.models.employee import Employee, EmployeeRole
from backend.models.employee_shift import EmployeeShift
from backend.models.resident import Resident
from backend.models.resident_assignment import AssignmentType, ResidentAssignment
from backend.schemas.resident_assignment import (
    AssignmentCreate,
    AssignmentUpdate,
    BulkAssignmentItem,
)
from backend.services.assignment_service import AssignmentService, _shift_state

NOW = datetime.now(timezone.utc)


class _StubClient:
    def table(self, _name):
        return object()


class FakeAssignmentRepository:
    def __init__(self, rows=None):
        self.rows = {str(r.id): r for r in (rows or [])}

    async def create(self, assignment):
        assignment = assignment.model_copy(update={"id": assignment.id or uuid4()})
        self.rows[str(assignment.id)] = assignment
        return assignment

    async def get_by_id(self, assignment_id):
        return self.rows.get(str(assignment_id))

    async def list_for_resident(self, resident_id, *, active_only=False):
        return [
            r
            for r in self.rows.values()
            if str(r.resident_id) == str(resident_id) and (r.active or not active_only)
        ]

    async def list_for_employee(self, employee_id, *, active_only=False):
        return [
            r
            for r in self.rows.values()
            if str(r.employee_id) == str(employee_id) and (r.active or not active_only)
        ]

    async def list_all(self, skip=0, limit=1000, *, active_only=False):
        return [r for r in self.rows.values() if r.active or not active_only]

    async def update(self, assignment_id, updates):
        row = self.rows.get(str(assignment_id))
        if row is None:
            return None
        updated = ResidentAssignment.model_validate({**row.model_dump(), **updates})
        self.rows[str(assignment_id)] = updated
        return updated

    async def delete(self, assignment_id):
        return self.rows.pop(str(assignment_id), None) is not None


class FakeSimpleRepository:
    def __init__(self, items=None):
        self.items = {str(i.id): i for i in (items or [])}

    async def get_by_id(self, item_id):
        return self.items.get(str(item_id))

    async def list_all(self, skip=0, limit=100):
        return list(self.items.values())


class FakeShiftRepository:
    def __init__(self, by_employee=None):
        self.by_employee = by_employee or {}

    async def list_for_parent(self, employee_id, skip=0, limit=100):
        return self.by_employee.get(str(employee_id), [])


class FakeRiskScoring:
    def __init__(self, scores=None):
        self.scores = scores or {}

    async def get_resident_score(self, resident_id):
        return self.scores.get(str(resident_id))


def make_resident(first="Maya", room="12A"):
    return Resident(id=uuid4(), first_name=first, last_name="Tamang", room_number=room)


def make_employee(first="Asha", role=EmployeeRole.REGISTERED_NURSE):
    return Employee(id=uuid4(), first_name=first, last_name="Gurung", role=role, active=True)


def build_service(*, residents=(), employees=(), assignments=(), shifts=None, scores=None):
    service = AssignmentService(_StubClient(), risk_scoring_service=FakeRiskScoring(scores))
    service._repository = FakeAssignmentRepository(list(assignments))
    service._resident_repository = FakeSimpleRepository(list(residents))
    service._employee_repository = FakeSimpleRepository(list(employees))
    service._shift_repository = FakeShiftRepository(shifts)
    return service


@pytest.mark.anyio
async def test_assigning_a_carer_links_the_two():
    resident, employee = make_resident(), make_employee()
    service = build_service(residents=[resident], employees=[employee])

    created = await service.create_assignment(
        str(resident.id),
        AssignmentCreate(employee_id=employee.id, assignment_type=AssignmentType.PRIMARY),
    )
    assert str(created.resident_id) == str(resident.id)
    assert str(created.employee_id) == str(employee.id)
    assert created.active


@pytest.mark.anyio
async def test_a_resident_cannot_have_two_primary_carers():
    """The point of a key worker is that there is exactly one name to call."""
    resident = make_resident()
    asha, bikash = make_employee("Asha"), make_employee("Bikash")
    service = build_service(residents=[resident], employees=[asha, bikash])

    await service.create_assignment(
        str(resident.id),
        AssignmentCreate(employee_id=asha.id, assignment_type=AssignmentType.PRIMARY),
    )
    with pytest.raises(HTTPException) as exc:
        await service.create_assignment(
            str(resident.id),
            AssignmentCreate(employee_id=bikash.id, assignment_type=AssignmentType.PRIMARY),
        )
    assert exc.value.status_code == 409
    assert "primary carer" in exc.value.detail


@pytest.mark.anyio
async def test_a_second_secondary_carer_is_fine():
    resident = make_resident()
    asha, bikash = make_employee("Asha"), make_employee("Bikash")
    service = build_service(residents=[resident], employees=[asha, bikash])

    await service.create_assignment(
        str(resident.id),
        AssignmentCreate(employee_id=asha.id, assignment_type=AssignmentType.PRIMARY),
    )
    await service.create_assignment(
        str(resident.id),
        AssignmentCreate(employee_id=bikash.id, assignment_type=AssignmentType.SECONDARY),
    )
    team = await service.get_care_team(str(resident.id))
    assert len(team.members) == 2


@pytest.mark.anyio
async def test_the_same_person_cannot_be_assigned_twice():
    """A duplicate would double-count them in every caseload figure."""
    resident, employee = make_resident(), make_employee()
    service = build_service(residents=[resident], employees=[employee])

    await service.create_assignment(str(resident.id), AssignmentCreate(employee_id=employee.id))
    with pytest.raises(HTTPException) as exc:
        await service.create_assignment(
            str(resident.id),
            AssignmentCreate(employee_id=employee.id, assignment_type=AssignmentType.RELIEF),
        )
    assert exc.value.status_code == 409
    assert "already assigned" in exc.value.detail


@pytest.mark.anyio
async def test_unknown_resident_or_employee_is_rejected():
    employee = make_employee()
    service = build_service(employees=[employee])
    with pytest.raises(HTTPException) as exc:
        await service.create_assignment(str(uuid4()), AssignmentCreate(employee_id=employee.id))
    assert exc.value.status_code == 404

    resident = make_resident()
    service = build_service(residents=[resident])
    with pytest.raises(HTTPException) as exc:
        await service.create_assignment(str(resident.id), AssignmentCreate(employee_id=uuid4()))
    assert exc.value.status_code == 404


@pytest.mark.anyio
async def test_setting_an_end_date_closes_the_assignment():
    """Ending should not leave the row still counted as live."""
    resident, employee = make_resident(), make_employee()
    service = build_service(residents=[resident], employees=[employee])
    created = await service.create_assignment(
        str(resident.id), AssignmentCreate(employee_id=employee.id)
    )

    updated = await service.update_assignment(
        str(resident.id), str(created.id), AssignmentUpdate(end_date=date(2026, 6, 30))
    )
    assert updated.active is False


@pytest.mark.anyio
async def test_an_ended_assignment_is_kept_not_erased():
    resident, employee = make_resident(), make_employee()
    service = build_service(residents=[resident], employees=[employee])
    created = await service.create_assignment(
        str(resident.id), AssignmentCreate(employee_id=employee.id)
    )
    await service.update_assignment(
        str(resident.id), str(created.id), AssignmentUpdate(end_date=date(2026, 6, 30))
    )

    team = await service.get_care_team(str(resident.id))
    assert len(team.members) == 1
    assert team.members[0].active is False
    assert team.has_primary is False


@pytest.mark.anyio
async def test_an_assignment_belonging_to_another_resident_is_not_reachable():
    """Prevents editing someone else's assignment by guessing its id."""
    resident_a, resident_b = make_resident("Maya"), make_resident("Sita")
    employee = make_employee()
    service = build_service(residents=[resident_a, resident_b], employees=[employee])
    created = await service.create_assignment(
        str(resident_a.id), AssignmentCreate(employee_id=employee.id)
    )

    with pytest.raises(HTTPException) as exc:
        await service.update_assignment(
            str(resident_b.id), str(created.id), AssignmentUpdate(notes="hijacked")
        )
    assert exc.value.status_code == 404


@pytest.mark.anyio
async def test_care_team_reports_who_is_on_shift_now():
    resident = make_resident()
    on, off = make_employee("Asha"), make_employee("Bikash")
    shifts = {
        str(on.id): [
            EmployeeShift(
                id=uuid4(), shift_start=NOW - timedelta(hours=1), shift_end=NOW + timedelta(hours=7)
            )
        ],
        str(off.id): [
            EmployeeShift(
                id=uuid4(), shift_start=NOW + timedelta(days=2), shift_end=NOW + timedelta(days=2, hours=8)
            )
        ],
    }
    service = build_service(residents=[resident], employees=[on, off], shifts=shifts)
    await service.create_assignment(
        str(resident.id),
        AssignmentCreate(employee_id=on.id, assignment_type=AssignmentType.PRIMARY),
    )
    await service.create_assignment(str(resident.id), AssignmentCreate(employee_id=off.id))

    team = await service.get_care_team(str(resident.id))
    assert team.on_shift_count == 1
    assert team.has_primary
    by_name = {m.first_name: m for m in team.members}
    assert by_name["Asha"].on_shift_now is True
    assert by_name["Bikash"].on_shift_now is False
    assert by_name["Bikash"].next_shift_start is not None


@pytest.mark.anyio
async def test_care_team_puts_the_primary_first():
    resident = make_resident()
    secondary, primary = make_employee("Zara"), make_employee("Asha")
    service = build_service(residents=[resident], employees=[secondary, primary])
    await service.create_assignment(str(resident.id), AssignmentCreate(employee_id=secondary.id))
    await service.create_assignment(
        str(resident.id),
        AssignmentCreate(employee_id=primary.id, assignment_type=AssignmentType.PRIMARY),
    )

    team = await service.get_care_team(str(resident.id))
    assert team.members[0].assignment_type == AssignmentType.PRIMARY


@pytest.mark.anyio
async def test_care_team_of_a_resident_with_nobody():
    resident = make_resident()
    service = build_service(residents=[resident])
    team = await service.get_care_team(str(resident.id))
    assert team.members == []
    assert team.has_primary is False


@pytest.mark.anyio
async def test_caseload_is_ordered_by_risk_and_totals_the_load():

    class Score:
        def __init__(self, resident_id, score, band):
            self.resident_id = resident_id
            self.score = score
            self.band = band

    low, high = make_resident("Low"), make_resident("High")
    employee = make_employee()
    scores = {
        str(low.id): Score(low.id, 20, "Low"),
        str(high.id): Score(high.id, 88, "Critical"),
    }
    service = build_service(
        residents=[low, high], employees=[employee], scores=scores, shifts={}
    )
    await service.create_assignment(str(low.id), AssignmentCreate(employee_id=employee.id))
    await service.create_assignment(
        str(high.id),
        AssignmentCreate(employee_id=employee.id, assignment_type=AssignmentType.PRIMARY),
    )

    caseload = await service.get_caseload(str(employee.id))
    assert [r.first_name for r in caseload.residents] == ["High", "Low"]
    assert caseload.total_risk_load == 108
    assert caseload.primary_count == 1


@pytest.mark.anyio
async def test_coverage_finds_residents_without_a_primary_carer():
    class Score:
        def __init__(self, resident_id, score, band):
            self.resident_id = resident_id
            self.score = score
            self.band = band

    covered, uncovered, alone = make_resident("Covered"), make_resident("Uncovered"), make_resident("Alone")
    employee, idle = make_employee("Asha"), make_employee("Idle", EmployeeRole.KITCHEN_STAFF)
    scores = {
        str(uncovered.id): Score(uncovered.id, 70, "High"),
        str(alone.id): Score(alone.id, 30, "Medium"),
    }
    service = build_service(
        residents=[covered, uncovered, alone],
        employees=[employee, idle],
        scores=scores,
        shifts={},
    )
    await service.create_assignment(
        str(covered.id),
        AssignmentCreate(employee_id=employee.id, assignment_type=AssignmentType.PRIMARY),
    )
    # Uncovered has a secondary but no primary; Alone has nobody.
    await service.create_assignment(str(uncovered.id), AssignmentCreate(employee_id=employee.id))

    report = await service.get_coverage_report()
    assert report.total_residents == 3
    assert report.residents_with_primary == 1
    assert report.residents_without_primary == 2
    assert report.residents_with_no_carer == 1

    # Highest risk first — the most actionable gap is the top row.
    assert [r.first_name for r in report.unassigned] == ["Uncovered", "Alone"]
    assert report.unassigned[0].has_any_carer is True
    assert report.unassigned[1].has_any_carer is False

    # The kitchen hand holds no caseload, which is expected but worth showing.
    assert [e.first_name for e in report.staff_without_caseload] == ["Idle"]


def test_shift_state_detects_a_current_shift():
    shifts = [
        EmployeeShift(
            id=uuid4(), shift_start=NOW - timedelta(hours=2), shift_end=NOW + timedelta(hours=6)
        )
    ]
    on_now, _, _ = _shift_state(shifts, NOW)
    assert on_now is True


def test_shift_state_picks_the_soonest_future_shift():
    soon = NOW + timedelta(hours=3)
    later = NOW + timedelta(days=4)
    shifts = [
        EmployeeShift(id=uuid4(), shift_start=later, shift_end=later + timedelta(hours=8)),
        EmployeeShift(id=uuid4(), shift_start=soon, shift_end=soon + timedelta(hours=8)),
    ]
    on_now, next_start, _ = _shift_state(shifts, NOW)
    assert on_now is False
    assert next_start == soon


def test_shift_state_handles_naive_datetimes():
    naive_start = (NOW - timedelta(hours=1)).replace(tzinfo=None)
    naive_end = (NOW + timedelta(hours=5)).replace(tzinfo=None)
    shifts = [EmployeeShift(id=uuid4(), shift_start=naive_start, shift_end=naive_end)]
    on_now, _, _ = _shift_state(shifts, NOW)
    assert on_now is True


def test_shift_state_with_no_shifts():
    assert _shift_state([], NOW) == (False, None, None)


@pytest.mark.anyio
async def test_confirming_a_plan_creates_every_assignment():
    residents = [make_resident(name) for name in ("Maya", "Gita")]
    employees = [make_employee(name) for name in ("Asha", "Deepa")]
    service = build_service(residents=residents, employees=employees)

    result = await service.create_many(
        [
            BulkAssignmentItem(resident_id=r.id, employee_id=e.id)
            for r, e in zip(residents, employees)
        ]
    )

    assert len(result.created) == 2
    assert result.failed == []
    assert all(a.assignment_type == AssignmentType.PRIMARY for a in result.created)
    assert all(a.start_date is not None for a in result.created)


@pytest.mark.anyio
async def test_a_rejected_line_does_not_cost_the_user_the_rest():
    """The reason this is not all-or-nothing."""
    taken, free = make_resident("Maya"), make_resident("Gita")
    existing_carer = make_employee("Asha")
    new_carer = make_employee("Deepa")
    service = build_service(
        residents=[taken, free],
        employees=[existing_carer, new_carer],
        assignments=[
            ResidentAssignment(
                id=uuid4(),
                resident_id=taken.id,
                employee_id=existing_carer.id,
                assignment_type=AssignmentType.PRIMARY,
            )
        ],
    )

    result = await service.create_many(
        [
            BulkAssignmentItem(resident_id=taken.id, employee_id=new_carer.id),
            BulkAssignmentItem(resident_id=free.id, employee_id=new_carer.id),
        ]
    )

    assert len(result.created) == 1
    assert str(result.created[0].resident_id) == str(free.id)
    assert len(result.failed) == 1
    assert str(result.failed[0].resident_id) == str(taken.id)
    # The message has to say what to do about it, not merely that it failed.
    assert "already has a primary carer" in result.failed[0].reason


@pytest.mark.anyio
async def test_the_one_primary_rule_holds_within_a_single_batch():
    resident = make_resident()
    first, second = make_employee("Asha"), make_employee("Deepa")
    service = build_service(residents=[resident], employees=[first, second])

    result = await service.create_many(
        [
            BulkAssignmentItem(resident_id=resident.id, employee_id=first.id),
            BulkAssignmentItem(resident_id=resident.id, employee_id=second.id),
        ]
    )

    assert len(result.created) == 1
    assert len(result.failed) == 1


@pytest.mark.anyio
async def test_a_line_naming_someone_who_does_not_exist_is_reported_not_raised():
    resident = make_resident()
    service = build_service(residents=[resident], employees=[])

    result = await service.create_many(
        [BulkAssignmentItem(resident_id=resident.id, employee_id=uuid4())]
    )

    assert result.created == []
    assert "not found" in result.failed[0].reason.lower()


@pytest.mark.anyio
async def test_confirming_nothing_is_not_an_error():
    service = build_service()
    result = await service.create_many([])
    assert result.created == [] and result.failed == []
