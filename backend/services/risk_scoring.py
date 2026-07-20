import asyncio
from datetime import datetime, timedelta, timezone

from supabase import AsyncClient

from backend.models.assistance import AssistanceLevel, ResidentAssistance
from backend.models.behaviour import ResidentBehaviour
from backend.models.fall_risk import ResidentFallRisk, RiskLevel
from backend.models.incident import IncidentSeverity, ResidentIncident
from backend.models.resident import CognitiveStatus, Resident
from backend.repositories.base import SupabaseRepository
from backend.repositories.resident_repository import ResidentRepository
from backend.schemas.risk_score import RiskScoreBreakdownItem, RiskScoreOut

# Weighted-sum scoring algorithm: each signal contributes a fixed number of
# points, the points are added up, then the total is clipped to 0-100. These
# weights are a starting guess (not learned from data) -- tune by eye once
# real resident history exists.
COGNITIVE_STATUS_POINTS = {
    CognitiveStatus.COGNITIVE: 0,
    CognitiveStatus.NON_COGNITIVE: 10,
    CognitiveStatus.DISABLED_COGNITIVE: 15,
    CognitiveStatus.DISABLED_NON_COGNITIVE: 20,
}
FALL_RISK_POINTS = {
    RiskLevel.LOW: 0,
    RiskLevel.MEDIUM: 15,
    RiskLevel.HIGH: 30,
}
ASSISTANCE_POINTS = {
    AssistanceLevel.INDEPENDENT: 0,
    AssistanceLevel.SINGLE_ASSIST: 10,
    AssistanceLevel.DOUBLE_ASSIST: 20,
}
INCIDENT_SEVERITY_POINTS = {
    IncidentSeverity.LOW: 1,
    IncidentSeverity.MEDIUM: 2,
    IncidentSeverity.HIGH: 3,
    IncidentSeverity.CRITICAL: 5,
}
INCIDENT_POINTS_MULTIPLIER = 5
INCIDENT_POINTS_CAP = 30
INCIDENT_LOOKBACK_DAYS = 90

BEHAVIOUR_POINTS_PER_EVENT = 5
BEHAVIOUR_POINTS_CAP = 20
BEHAVIOUR_LOOKBACK_DAYS = 30

BAND_THRESHOLDS = (
    (75, "Critical"),
    (50, "High"),
    (25, "Medium"),
    (0, "Low"),
)


def _band_for_score(score: int) -> str:
    for threshold, label in BAND_THRESHOLDS:
        if score >= threshold:
            return label
    return "Low"


def _as_aware(dt: datetime) -> datetime:
    # Some existing tables store `timestamp` (no timezone) rather than
    # `timestamptz`, so Supabase can return naive datetimes here. Treat
    # naive values as UTC rather than letting the comparison below crash.
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


class RiskScoringService:
    def __init__(self, client: AsyncClient):
        self._resident_repository = ResidentRepository(client)
        self._fall_risk_repository = SupabaseRepository(
            client, "resident_fall_risk", ResidentFallRisk, order_column="assessment_date"
        )
        self._incident_repository = SupabaseRepository(
            client, "resident_incidents", ResidentIncident, order_column="occurred_at"
        )
        self._assistance_repository = SupabaseRepository(
            client, "resident_assistance", ResidentAssistance, order_column="updated_at"
        )
        self._behaviour_repository = SupabaseRepository(
            client, "resident_behaviour", ResidentBehaviour, order_column="recorded_at"
        )

    async def score_resident(self, resident: Resident) -> RiskScoreOut:
        resident_id = str(resident.id)
        now = datetime.now(timezone.utc)

        breakdown: dict[str, RiskScoreBreakdownItem] = {}

        # These four lookups are independent -- fetch them concurrently
        # instead of one at a time, since each is a network round-trip to
        # Supabase.
        fall_risk_records, incidents, assistance_records, behaviour_records = await asyncio.gather(
            self._fall_risk_repository.list_for_parent(resident_id, 0, 1),
            self._incident_repository.list_for_parent(resident_id, 0, 100),
            self._assistance_repository.list_for_parent(resident_id, 0, 1),
            self._behaviour_repository.list_for_parent(resident_id, 0, 100),
        )

        cognitive_points = COGNITIVE_STATUS_POINTS.get(resident.cognitive_status, 0)
        breakdown["cognitive_status"] = RiskScoreBreakdownItem(
            value=str(resident.cognitive_status) if resident.cognitive_status else "Unknown",
            points=cognitive_points,
        )

        latest_fall_risk = fall_risk_records[0].risk_level if fall_risk_records else None
        fall_risk_points = FALL_RISK_POINTS.get(latest_fall_risk, 0)
        breakdown["fall_risk"] = RiskScoreBreakdownItem(
            value=str(latest_fall_risk) if latest_fall_risk else "No assessment on record",
            points=fall_risk_points,
        )

        cutoff = now - timedelta(days=INCIDENT_LOOKBACK_DAYS)
        recent_incidents = [i for i in incidents if _as_aware(i.occurred_at) >= cutoff]
        raw_incident_points = sum(
            INCIDENT_SEVERITY_POINTS.get(i.severity, 0) for i in recent_incidents
        ) * INCIDENT_POINTS_MULTIPLIER
        incident_points = min(raw_incident_points, INCIDENT_POINTS_CAP)
        breakdown["recent_incidents_90d"] = RiskScoreBreakdownItem(
            value=f"{len(recent_incidents)} incident(s) in last {INCIDENT_LOOKBACK_DAYS} days",
            points=incident_points,
        )

        latest_assistance = assistance_records[0].assistance_level if assistance_records else None
        assistance_points = ASSISTANCE_POINTS.get(latest_assistance, 0)
        breakdown["assistance_level"] = RiskScoreBreakdownItem(
            value=str(latest_assistance) if latest_assistance else "No assessment on record",
            points=assistance_points,
        )

        behaviour_cutoff = now - timedelta(days=BEHAVIOUR_LOOKBACK_DAYS)
        recent_behaviour_count = sum(
            1 for b in behaviour_records if _as_aware(b.recorded_at) >= behaviour_cutoff
        )
        behaviour_points = min(
            recent_behaviour_count * BEHAVIOUR_POINTS_PER_EVENT, BEHAVIOUR_POINTS_CAP
        )
        breakdown["recent_behaviour_30d"] = RiskScoreBreakdownItem(
            value=f"{recent_behaviour_count} event(s) in last {BEHAVIOUR_LOOKBACK_DAYS} days",
            points=behaviour_points,
        )

        total = min(sum(item.points for item in breakdown.values()), 100)

        return RiskScoreOut(
            resident_id=resident.id,
            first_name=resident.first_name,
            last_name=resident.last_name,
            score=total,
            band=_band_for_score(total),
            breakdown=breakdown,
        )

    async def get_resident_score(self, resident_id: str) -> RiskScoreOut | None:
        resident = await self._resident_repository.get_by_id(resident_id)
        if resident is None:
            return None
        return await self.score_resident(resident)

    async def list_scores(self, skip: int = 0, limit: int = 100) -> list[RiskScoreOut]:
        residents = await self._resident_repository.list_all(skip, limit)
        # Each resident's score is independent, so compute them concurrently
        # rather than awaiting one at a time.
        scores = await asyncio.gather(*(self.score_resident(r) for r in residents))
        return sorted(scores, key=lambda s: s.score, reverse=True)
