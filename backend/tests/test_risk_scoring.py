"""The AHP-weighted risk model."""

from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

import pytest

from backend.config.risk_weights import (
    BEHAVIOUR_SATURATION,
    INCIDENT_SATURATION,
    RISK_WEIGHTS,
)
from backend.models.assistance import AssistanceLevel, ResidentAssistance
from backend.models.behaviour import ResidentBehaviour
from backend.models.fall_risk import ResidentFallRisk, RiskLevel
from backend.models.incident import IncidentSeverity, ResidentIncident
from backend.models.resident import CognitiveStatus, Resident
from backend.services.risk_scoring import RiskScoringService, _saturating

NOW = datetime.now(timezone.utc)


class _StubClient:
    """Enough of the Supabase client for the repositories' constructors."""

    def table(self, _name):
        return object()


class _StubRepository:
    def __init__(self, records):
        self._records = records

    async def list_for_parent(self, _parent_id, _skip=0, _limit=100):
        return self._records


def build_service(
    *,
    fall_risk: RiskLevel | None = None,
    incidents: list[IncidentSeverity] | None = None,
    assistance: AssistanceLevel | None = None,
    behaviour_events: int = 0,
    days_ago: int = 1,
) -> RiskScoringService:
    service = RiskScoringService(_StubClient())
    resident_id = uuid4()
    occurred = NOW - timedelta(days=days_ago)

    service._fall_risk_repository = _StubRepository(
        [ResidentFallRisk(resident_id=resident_id, risk_level=fall_risk, assessment_date=date.today())]
        if fall_risk
        else []
    )
    service._incident_repository = _StubRepository(
        [
            ResidentIncident(
                resident_id=resident_id,
                incident_type="Fall",
                severity=severity,
                description="test",
                occurred_at=occurred,
            )
            for severity in (incidents or [])
        ]
    )
    service._assistance_repository = _StubRepository(
        [ResidentAssistance(resident_id=resident_id, assistance_level=assistance)]
        if assistance
        else []
    )
    service._behaviour_repository = _StubRepository(
        [
            ResidentBehaviour(resident_id=resident_id, recorded_at=occurred)
            for _ in range(behaviour_events)
        ]
    )
    return service


def resident(cognitive: CognitiveStatus | None = None) -> Resident:
    return Resident(
        id=uuid4(), first_name="Test", last_name="Resident", cognitive_status=cognitive
    )


async def score(service, res):
    return await service.score_resident(res)


@pytest.mark.anyio
async def test_breakdown_sums_exactly_to_the_score():
    service = build_service(
        fall_risk=RiskLevel.HIGH,
        incidents=[IncidentSeverity.CRITICAL, IncidentSeverity.HIGH],
        assistance=AssistanceLevel.DOUBLE_ASSIST,
        behaviour_events=6,
    )
    result = await score(service, resident(CognitiveStatus.DISABLED_NON_COGNITIVE))
    assert sum(item.points for item in result.breakdown.values()) == result.score


@pytest.mark.anyio
async def test_worst_case_resident_scores_one_hundred():
    service = build_service(
        fall_risk=RiskLevel.HIGH,
        incidents=[IncidentSeverity.CRITICAL, IncidentSeverity.CRITICAL],
        assistance=AssistanceLevel.DOUBLE_ASSIST,
        behaviour_events=10,
    )
    result = await score(service, resident(CognitiveStatus.DISABLED_NON_COGNITIVE))
    assert result.score == 100
    assert result.band == "Critical"


@pytest.mark.anyio
async def test_resident_with_no_signals_scores_zero():
    result = await score(build_service(), resident(CognitiveStatus.COGNITIVE))
    assert result.score == 0
    assert result.band == "Low"


@pytest.mark.anyio
async def test_missing_assessments_do_not_invent_risk():
    result = await score(build_service(), resident(None))
    assert result.breakdown["fall_risk"].points == 0
    assert result.breakdown["fall_risk"].value == "No assessment on record"


@pytest.mark.anyio
async def test_score_is_monotonic_in_fall_risk():
    scores = []
    for level in (RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH):
        result = await score(build_service(fall_risk=level), resident(CognitiveStatus.COGNITIVE))
        scores.append(result.score)
    assert scores[0] < scores[1] < scores[2]


@pytest.mark.anyio
async def test_each_criterion_contributes_its_ahp_weight_at_full_severity():
    service = build_service(fall_risk=RiskLevel.HIGH)
    result = await score(service, resident(CognitiveStatus.COGNITIVE))
    assert result.score == round(100 * RISK_WEIGHTS["fall_risk"])


@pytest.mark.anyio
async def test_incidents_outside_the_window_are_ignored():
    recent = build_service(incidents=[IncidentSeverity.CRITICAL], days_ago=5)
    stale = build_service(incidents=[IncidentSeverity.CRITICAL], days_ago=200)
    assert (await score(recent, resident())).score > (await score(stale, resident())).score


@pytest.mark.anyio
async def test_incident_signal_saturates():
    many = build_service(incidents=[IncidentSeverity.CRITICAL] * 12)
    enough = build_service(incidents=[IncidentSeverity.CRITICAL] * 2)
    assert (await score(many, resident())).score == (await score(enough, resident())).score


@pytest.mark.anyio
async def test_breakdown_exposes_weight_and_normalised_severity():
    service = build_service(assistance=AssistanceLevel.SINGLE_ASSIST)
    result = await score(service, resident(CognitiveStatus.COGNITIVE))
    item = result.breakdown["assistance_level"]
    assert item.normalised == pytest.approx(0.5)
    assert item.weight == pytest.approx(RISK_WEIGHTS["assistance_level"], abs=1e-4)


@pytest.mark.parametrize(
    "value,ceiling,expected",
    [
        (0, 4, 0.0),
        (2, 4, 0.5),
        (4, 4, 1.0),
        (40, 4, 1.0),
        (1, 0, 0.0),
    ],
)
def test_saturating(value, ceiling, expected):
    assert _saturating(value, ceiling) == pytest.approx(expected)


def test_saturation_constants_are_sane():
    assert INCIDENT_SATURATION > 0
    assert BEHAVIOUR_SATURATION > 0
