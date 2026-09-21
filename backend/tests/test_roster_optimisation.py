"""Shift ranking (SAW + lexicographic) and the roster recommendation built on it."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from backend.models.employee import Employee, EmployeeRole
from backend.models.employee_shift import EmployeeShift
from backend.services.roster_optimisation import RosterOptimisationService
from backend.services.shift_matching import rank_shift_candidates

MONDAY = datetime(2026, 3, 2, 7, 0, tzinfo=timezone.utc)


class _StubClient:
    def table(self, _name):
        return object()


def make_employee(first: str, role: EmployeeRole | None = None) -> Employee:
    return Employee(id=uuid4(), first_name=first, last_name="Staff", role=role, active=True)


def make_shift(hour_offset: int, hours: int = 8, role: str | None = None) -> EmployeeShift:
    start = MONDAY + timedelta(hours=hour_offset)
    return EmployeeShift(
        id=uuid4(), shift_start=start, shift_end=start + timedelta(hours=hours), role=role
    )


def profile(employee, *, care_load=0.0, week_hours=0.0, shifts=None):
    return {
        "employee": employee,
        "shifts": shifts or [],
        "care_load": care_load,
        "residents": 0,
        "week_hours": week_hours,
    }


def build_service(shifts, profiles) -> RosterOptimisationService:
    service = RosterOptimisationService(_StubClient(), risk_scoring_service=None)

    async def _load_shifts(*_args, **_kwargs):
        return shifts

    async def _employee_profile(employee, _week_key):
        return profiles[str(employee.id)]

    async def _list_all(_skip=0, _limit=100):
        return [p["employee"] for p in profiles.values()]

    service._load_shifts = _load_shifts
    service._employee_profile = _employee_profile
    service._employee_repository.list_all = _list_all
    return service


def row(name, conflict=False, role_match=True, care_load=0.0, week_hours=0.0):
    return dict(name=name, conflict=conflict, role_match=role_match, care_load=care_load, week_hours=week_hours)


def test_a_conflict_ranks_last_even_with_the_best_saw_score():
    rows = [
        row("A", care_load=30, week_hours=20),
        row("B", care_load=50, week_hours=15),
        row("C", conflict=True, care_load=10, week_hours=10),  # lowest workload
    ]
    ranked = rank_shift_candidates(rows)

    assert [r["name"] for r in ranked] == ["A", "B", "C"]
    assert ranked[2]["saw_score"] > ranked[0]["saw_score"]  # C scores best, still last
    assert [r["rank"] for r in ranked] == [1, 2, 3]


def test_role_match_outranks_saw_score():
    ranked = rank_shift_candidates([row("wrong", role_match=False), row("right", care_load=99, week_hours=40)])
    assert ranked[0]["name"] == "right"


def test_the_saw_breakdown_adds_up_to_the_score():
    ranked = rank_shift_candidates([row("A", care_load=30, week_hours=20), row("B", care_load=50)])
    for r in ranked:
        assert sum(i["contribution"] for i in r["breakdown"]) == pytest.approx(r["saw_score"], abs=1e-3)


@pytest.mark.anyio
async def test_nobody_is_double_booked():
    """Two overlapping shifts and two staff: each employee gets one."""
    first, second = make_shift(0), make_shift(2)
    a, b = make_employee("A"), make_employee("B")
    profiles = {str(a.id): profile(a), str(b.id): profile(b)}

    result = await build_service([second, first], profiles).optimise()

    chosen = [x.employee_id for x in result.assignments]
    assert None not in chosen and len(set(chosen)) == 2
    assert result.assignments[0].shift_id == first.id  # chronological order


@pytest.mark.anyio
async def test_the_only_free_employee_is_not_given_two_overlapping_shifts():
    first, second = make_shift(0), make_shift(2)
    solo = make_employee("Solo")

    result = await build_service([first, second], {str(solo.id): profile(solo)}).optimise()

    assert result.assignments[0].employee_id == solo.id
    assert result.assignments[1].employee_id is None
    assert result.assignments[1].unassigned_reason == "Every candidate has a clashing shift"


@pytest.mark.anyio
async def test_back_to_back_shifts_can_go_to_the_same_person():
    first, second = make_shift(0), make_shift(8)
    solo = make_employee("Solo")

    result = await build_service([first, second], {str(solo.id): profile(solo)}).optimise()

    assert all(x.employee_id == solo.id for x in result.assignments)


@pytest.mark.anyio
async def test_an_existing_clashing_shift_rules_the_employee_out():
    target = make_shift(0)
    busy, free = make_employee("Busy"), make_employee("Free")
    profiles = {
        str(busy.id): profile(busy, shifts=[make_shift(4)]),
        str(free.id): profile(free, care_load=300, week_hours=40),
    }

    result = await build_service([target], profiles).optimise()

    assert result.assignments[0].employee_id == free.id


@pytest.mark.anyio
async def test_no_shifts_returns_an_empty_result_rather_than_failing():
    a = make_employee("A")
    result = await build_service([], {str(a.id): profile(a)}).optimise()
    assert result.assignments == [] and result.shifts_considered == 0
