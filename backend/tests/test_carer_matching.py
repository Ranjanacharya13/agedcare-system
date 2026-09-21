"""Suggesting who should care for whom: SAW score + lexicographic ranking."""

from uuid import uuid4

import pytest

from backend.models.employee import EmployeeRole
from backend.models.resident_assignment import AssignmentType, ResidentAssignment
from backend.services.carer_matching import CarerMatchingService
from backend.tests.test_assignments import (
    FakeAssignmentRepository,
    FakeRiskScoring,
    FakeSimpleRepository,
    _StubClient,
    make_employee,
    make_resident,
)


class _Score:
    """Minimal stand-in for RiskScoreOut: the matcher only reads these fields."""

    def __init__(self, resident_id, score, band="High"):
        self.resident_id = resident_id
        self.score = score
        self.band = band


def build_service(*, residents=(), employees=(), assignments=(), scores=None):
    service = CarerMatchingService(_StubClient(), risk_scoring_service=FakeRiskScoring(scores))
    service._assignment_repository = FakeAssignmentRepository(list(assignments))
    service._resident_repository = FakeSimpleRepository(list(residents))
    service._employee_repository = FakeSimpleRepository(list(employees))
    return service


def primary(resident, employee, active=True):
    return ResidentAssignment(
        id=uuid4(),
        resident_id=resident.id,
        employee_id=employee.id,
        assignment_type=AssignmentType.PRIMARY,
        active=active,
    )


@pytest.mark.anyio
async def test_the_least_loaded_carer_is_ranked_first():
    needs_a_carer = make_resident("Gita")
    held = make_resident("Maya")
    busy = make_employee("Bikash")
    free = make_employee("Asha")
    service = build_service(
        residents=[needs_a_carer, held],
        employees=[busy, free],
        assignments=[primary(held, busy)],
        scores={str(held.id): _Score(held.id, 80)},
    )

    ranked = await service.rank_candidates_for_resident(str(needs_a_carer.id))

    assert [c.first_name for c in ranked] == ["Asha", "Bikash"]
    assert [c.rank for c in ranked] == [1, 2]
    assert ranked[0].saw_score > ranked[1].saw_score
    assert ranked[1].current_risk_load == 80


@pytest.mark.anyio
async def test_a_non_clinical_role_ranks_last_even_with_no_workload():
    resident = make_resident()
    held = make_resident("Maya")
    nurse = make_employee("Asha", EmployeeRole.REGISTERED_NURSE)
    kitchen = make_employee("Kiran", EmployeeRole.KITCHEN_STAFF)
    service = build_service(
        residents=[resident, held],
        employees=[kitchen, nurse],
        assignments=[primary(held, nurse)],  # the nurse is busier than the kitchen hand
        scores={str(held.id): _Score(held.id, 90)},
    )

    ranked = await service.rank_candidates_for_resident(str(resident.id))

    assert [c.first_name for c in ranked] == ["Asha", "Kiran"]
    assert ranked[1].role_suitable is False


@pytest.mark.anyio
async def test_inactive_and_already_assigned_carers_are_not_suggested():
    resident = make_resident()
    already_there = make_employee("Asha")
    inactive = make_employee("Ina")
    inactive.active = False
    other = make_employee("Deepa")
    service = build_service(
        residents=[resident],
        employees=[already_there, inactive, other],
        assignments=[primary(resident, already_there)],
    )

    ranked = await service.rank_candidates_for_resident(str(resident.id))

    assert [c.first_name for c in ranked] == ["Deepa"]


@pytest.mark.anyio
async def test_every_candidate_has_a_reason_and_a_breakdown_that_adds_up_to_its_score():
    resident = make_resident()
    service = build_service(
        residents=[resident], employees=[make_employee("Asha"), make_employee("Bo")]
    )

    for c in await service.rank_candidates_for_resident(str(resident.id)):
        assert c.reason
        assert sum(i.contribution for i in c.breakdown) == pytest.approx(c.saw_score, abs=1e-3)


@pytest.mark.anyio
async def test_a_high_risk_resident_ranks_the_nurse_above_a_lower_skilled_role():
    resident = make_resident()
    nurse = make_employee("Asha", EmployeeRole.REGISTERED_NURSE)
    manager = make_employee("Mo", EmployeeRole.MANAGER)
    service = build_service(
        residents=[resident],
        employees=[manager, nurse],
        scores={str(resident.id): _Score(resident.id, 95)},
    )

    ranked = await service.rank_candidates_for_resident(str(resident.id))

    assert ranked[0].first_name == "Asha"


@pytest.mark.anyio
async def test_only_residents_without_a_primary_carer_are_proposed_for():
    covered = make_resident("Covered")
    gap = make_resident("Gap")
    ended = make_resident("Ended")
    a, b = make_employee("Asha"), make_employee("Bo")
    service = build_service(
        residents=[covered, gap, ended],
        employees=[a, b],
        assignments=[primary(covered, a), primary(ended, b, active=False)],
    )

    plan = await service.suggest_assignments()

    assert {s.first_name for s in plan.suggestions} == {"Gap", "Ended"}


@pytest.mark.anyio
async def test_the_most_urgent_resident_is_first_and_each_pick_adds_to_that_carers_load():
    calm, unwell = make_resident("Calm"), make_resident("Unwell")
    a, b = make_employee("Asha"), make_employee("Bo")
    service = build_service(
        residents=[calm, unwell],
        employees=[a, b],
        scores={str(calm.id): _Score(calm.id, 10), str(unwell.id): _Score(unwell.id, 90)},
    )

    plan = await service.suggest_assignments()

    assert [s.first_name for s in plan.suggestions] == ["Unwell", "Calm"]
    # The second pick sees the first carer's new load, so it goes to the other nurse.
    assert plan.suggestions[0].employee_id != plan.suggestions[1].employee_id


@pytest.mark.anyio
async def test_no_staff_leaves_residents_unmatched_and_no_gaps_means_no_work():
    plan = await build_service(residents=[make_resident()]).suggest_assignments()
    assert plan.unmatched == 1 and plan.suggestions[0].employee_id is None

    empty = await build_service().suggest_assignments()
    assert empty.suggestions == [] and empty.unmatched == 0
