"""Suggesting who should care for whom: SAW score, then lexicographic ranking.

For one resident:
  1. reject inactive employees and anyone already on the resident's care team (hard rules)
  2. normalise the soft criteria across the remaining candidates
  3. SAW score = weighted sum of the normalised criteria (higher is better)
  4. rank lexicographically: suitable role first, then SAW score, then smaller caseload
"""

from __future__ import annotations

import asyncio

from supabase import AsyncClient

from backend.algorithms.lexicographic import rank
from backend.algorithms.saw import calculate_saw_score, normalize_all, saw_breakdown
from backend.models.employee import Employee, EmployeeRole
from backend.models.resident_assignment import AssignmentType
from backend.repositories.employee_repository import EmployeeRepository
from backend.repositories.resident_assignment_repository import (
    ResidentAssignmentRepository,
)
from backend.repositories.resident_repository import ResidentRepository
from backend.schemas.carer_suggestion import (
    CarerCandidateOut,
    CarerSuggestionOut,
    SuggestAssignmentsOut,
)
from backend.services.risk_scoring import RiskScoringService

# SAW weights. All three are 0..1 with 1 = best, and they sum to 1.0.
# Same 1.0 : 0.5 : 1.5 balance the old cost model used, scaled to sum to 1.
CARER_WEIGHTS = {
    "risk_load": 0.33,  # cost: total risk score of residents the carer already holds
    "caseload": 0.17,  # cost: number of residents the carer already holds
    "acuity_fit": 0.50,  # benefit: 1 - resident acuity x (1 - clinical skill of the role)
}

# Lexicographic priority, most important first: (field, higher_is_better).
# Active and not-already-on-the-team are hard rules applied before ranking.
CARER_PRIORITY = (
    ("role_suitable", True),  # 1. a caring role first
    ("saw_score", True),  # 2. best SAW score
    ("caseload", False),  # 3. tie-break: smaller caseload
)

NON_CARING_ROLES = frozenset(
    {EmployeeRole.KITCHEN_STAFF, EmployeeRole.LAUNDRY_STAFF, EmployeeRole.ADMINISTRATOR}
)

# Clinical skill of each role, 0..1 (higher = can safely care for sicker residents).
ROLE_SKILL = {
    EmployeeRole.REGISTERED_NURSE: 1.0,
    EmployeeRole.CARE_PLANNER: 0.7,
    EmployeeRole.CARE_COORDINATOR: 0.6,
    EmployeeRole.MANAGER: 0.4,
    EmployeeRole.ADMINISTRATOR: 0.0,
    EmployeeRole.KITCHEN_STAFF: 0.0,
    EmployeeRole.LAUNDRY_STAFF: 0.0,
}
UNKNOWN_ROLE_SKILL = 0.3

ALTERNATIVES_PER_RESIDENT = 6
MAX_RISK_SCORE = 100.0


class CarerMatchingService:
    def __init__(self, client: AsyncClient, risk_scoring_service: RiskScoringService):
        self._assignment_repository = ResidentAssignmentRepository(client)
        self._resident_repository = ResidentRepository(client)
        self._employee_repository = EmployeeRepository(client)
        self._risk_scoring_service = risk_scoring_service

    async def _staff_state(self) -> tuple[list[Employee], dict[str, dict]]:
        """Every active employee, with what they are already carrying."""
        employees, assignments = await asyncio.gather(
            self._employee_repository.list_all(0, 1000),
            self._assignment_repository.list_all(0, 5000, active_only=True),
        )
        active = [e for e in employees if e.active]

        held: dict[str, list[str]] = {}
        for assignment in assignments:
            if assignment.employee_id:
                held.setdefault(str(assignment.employee_id), []).append(
                    str(assignment.resident_id)
                )

        # Score each distinct resident once, not once per carer holding them.
        distinct = {rid for ids in held.values() for rid in ids}
        scored = await asyncio.gather(
            *(self._risk_scoring_service.get_resident_score(rid) for rid in distinct)
        )
        score_by_resident = {
            str(s.resident_id): s.score for s in scored if s is not None
        }

        state = {}
        for employee in active:
            resident_ids = held.get(str(employee.id), [])
            state[str(employee.id)] = {
                "employee": employee,
                "resident_ids": resident_ids,
                "risk_load": sum(score_by_resident.get(rid, 0) for rid in resident_ids),
                "caseload": len(resident_ids),
            }
        return active, state

    @staticmethod
    def _skill(employee: Employee) -> float:
        return ROLE_SKILL.get(employee.role, UNKNOWN_ROLE_SKILL)

    def _rank(self, staff_list: list[dict], resident_id: str, acuity: float) -> list[dict]:
        """Rank the carers who could take this resident, best first."""
        # Hard rule: someone already on the care team cannot be assigned again.
        candidates = [s for s in staff_list if resident_id not in s["resident_ids"]]
        if not candidates:
            return []

        # Normalise the cost criteria (lower value -> closer to 1).
        risk_n = normalize_all([s["risk_load"] for s in candidates])
        case_n = normalize_all([s["caseload"] for s in candidates])

        rows = []
        for staff, risk, case in zip(candidates, risk_n, case_n):
            employee = staff["employee"]
            # Already 0..1, so it needs no min-max step.
            acuity_fit = 1.0 - acuity * (1.0 - self._skill(employee))
            normalised = {"risk_load": risk, "caseload": case, "acuity_fit": acuity_fit}
            rows.append(
                {
                    "staff": staff,
                    "role_suitable": employee.role not in NON_CARING_ROLES,
                    # SAW score: higher value means a better candidate.
                    "saw_score": calculate_saw_score(normalised, CARER_WEIGHTS),
                    "caseload": staff["caseload"],
                    "normalised": normalised,
                    "breakdown": saw_breakdown(
                        normalised,
                        CARER_WEIGHTS,
                        {
                            "risk_load": staff["risk_load"],
                            "caseload": staff["caseload"],
                            "acuity_fit": round(acuity_fit, 2),
                        },
                    ),
                }
            )

        ranked = rank(rows, CARER_PRIORITY)
        for position, row in enumerate(ranked, start=1):
            row["rank"] = position
        return ranked

    @staticmethod
    def _reason(row: dict) -> str:
        """Plain-language justification, built from the criteria."""
        staff = row["staff"]
        bits = [
            "holds no residents yet"
            if staff["caseload"] == 0
            else f"currently {staff['caseload']} resident(s), risk load {staff['risk_load']}"
        ]
        bits.append(
            f"{staff['employee'].role or 'role unknown'}"
            if row["role_suitable"]
            else "not a clinical role"
        )
        best = max(row["breakdown"], key=lambda item: item["contribution"])
        bits.append(f"strongest criterion: {best['criterion']} ({best['normalised']:.2f})")
        return "; ".join(bits)

    @staticmethod
    def _candidate(row: dict) -> CarerCandidateOut:
        employee = row["staff"]["employee"]
        return CarerCandidateOut(
            employee_id=employee.id,
            first_name=employee.first_name,
            last_name=employee.last_name,
            role=employee.role,
            current_caseload=row["staff"]["caseload"],
            current_risk_load=row["staff"]["risk_load"],
            role_suitable=row["role_suitable"],
            saw_score=round(row["saw_score"], 4),
            rank=row["rank"],
            breakdown=row["breakdown"],
            reason=CarerMatchingService._reason(row),
        )

    async def rank_candidates_for_resident(
        self, resident_id: str, limit: int = 5
    ) -> list[CarerCandidateOut]:
        """Who could take this resident, best first."""
        (_, state), score = await asyncio.gather(
            self._staff_state(),
            self._risk_scoring_service.get_resident_score(resident_id),
        )
        acuity = (score.score / MAX_RISK_SCORE) if score else 0.0
        ranked = self._rank(list(state.values()), resident_id, acuity)
        return [self._candidate(row) for row in ranked[:limit]]

    async def suggest_assignments(self, limit: int = 50) -> SuggestAssignmentsOut:
        """Propose a primary carer for every resident who lacks one.

        Residents are handled one at a time, highest risk first. After each pick the carer's
        caseload and risk load go up, so the next resident sees the updated load.
        """
        residents, (employees, state) = await asyncio.gather(
            self._resident_repository.list_all(0, 1000),
            self._staff_state(),
        )
        assignments = await self._assignment_repository.list_all(0, 5000, active_only=True)

        with_primary = {
            str(a.resident_id)
            for a in assignments
            if a.assignment_type == AssignmentType.PRIMARY
        }
        gaps = [
            r for r in residents if r.active is not False and str(r.id) not in with_primary
        ][:limit]

        scores = await asyncio.gather(
            *(self._risk_scoring_service.get_resident_score(str(r.id)) for r in gaps)
        )
        score_by_id = {str(s.resident_id): s for s in scores if s is not None}
        gaps.sort(key=lambda r: -(score_by_id[str(r.id)].score if str(r.id) in score_by_id else 0))

        suggestions = []
        for resident in gaps:
            score = score_by_id.get(str(resident.id))
            acuity = (score.score / MAX_RISK_SCORE) if score else 0.0
            ranked = self._rank(list(state.values()), str(resident.id), acuity)
            common = dict(
                resident_id=resident.id,
                first_name=resident.first_name,
                last_name=resident.last_name,
                room_number=resident.room_number,
                risk_score=score.score if score else None,
                risk_band=score.band if score else None,
                alternatives=[self._candidate(r) for r in ranked[:ALTERNATIVES_PER_RESIDENT]],
            )
            if not ranked:
                suggestions.append(
                    CarerSuggestionOut(
                        **common, reason="No available staff member could be matched"
                    )
                )
                continue

            best = ranked[0]
            employee = best["staff"]["employee"]
            suggestions.append(
                CarerSuggestionOut(
                    **common,
                    employee_id=employee.id,
                    employee_name=f"{employee.first_name} {employee.last_name}",
                    employee_role=employee.role,
                    saw_score=round(best["saw_score"], 4),
                    reason=self._reason(best),
                )
            )
            # Remember this pick so the next resident sees the carer's new load.
            best["staff"]["resident_ids"].append(str(resident.id))
            best["staff"]["caseload"] += 1
            best["staff"]["risk_load"] += score.score if score else 0

        return SuggestAssignmentsOut(
            residents_needing_a_carer=len(gaps),
            candidates_considered=len(employees),
            suggestions=suggestions,
            unmatched=sum(1 for s in suggestions if s.employee_id is None),
        )
