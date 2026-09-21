"""Resident risk score, using Simple Additive Weighting (SAW).

    score = 100 x sum( weight_j x normalised_signal_j )

Each signal is normalised to 0..1 (1 = highest risk, so here a high score means high risk,
not "better"). The weights come from AHP (see config/risk_weights.py) and sum to 1.
"""

import asyncio
from datetime import datetime, timedelta, timezone

from supabase import AsyncClient

from backend.config.risk_weights import (
    BEHAVIOUR_LOOKBACK_DAYS,
    BEHAVIOUR_SATURATION,
    INCIDENT_LOOKBACK_DAYS,
    INCIDENT_SATURATION,
    RISK_WEIGHTS,
)
from backend.models.assistance import AssistanceLevel, ResidentAssistance
from backend.models.behaviour import ResidentBehaviour
from backend.models.fall_risk import ResidentFallRisk, RiskLevel
from backend.models.incident import IncidentSeverity, ResidentIncident
from backend.models.resident import CognitiveStatus, Resident
from backend.repositories.base import SupabaseRepository
from backend.repositories.resident_repository import ResidentRepository
from backend.schemas.risk_score import RiskScoreBreakdownItem, RiskScoreOut


COGNITIVE_STATUS_SEVERITY = {
    CognitiveStatus.COGNITIVE: 0.0,
    CognitiveStatus.NON_COGNITIVE: 0.5,
    CognitiveStatus.DISABLED_COGNITIVE: 0.75,
    CognitiveStatus.DISABLED_NON_COGNITIVE: 1.0,
}
FALL_RISK_SEVERITY = {
    RiskLevel.LOW: 0.0,
    RiskLevel.MEDIUM: 0.5,
    RiskLevel.HIGH: 1.0,
}
ASSISTANCE_SEVERITY = {
    AssistanceLevel.INDEPENDENT: 0.0,
    AssistanceLevel.SINGLE_ASSIST: 0.5,
    AssistanceLevel.DOUBLE_ASSIST: 1.0,
}
INCIDENT_SEVERITY_POINTS = {
    IncidentSeverity.LOW: 1,
    IncidentSeverity.MEDIUM: 2,
    IncidentSeverity.HIGH: 3,
    IncidentSeverity.CRITICAL: 5,
}

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
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def _saturating(value: float, ceiling: float) -> float:
    """Map a count onto [0, 1], flattening once it reaches the ceiling."""
    if ceiling <= 0:
        return 0.0
    return min(value / ceiling, 1.0)


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

        fall_risk_records, incidents, assistance_records, behaviour_records = await asyncio.gather(
            self._fall_risk_repository.list_for_parent(resident_id, 0, 1),
            self._incident_repository.list_for_parent(resident_id, 0, 100),
            self._assistance_repository.list_for_parent(resident_id, 0, 1),
            self._behaviour_repository.list_for_parent(resident_id, 0, 100),
        )


        latest_fall_risk = fall_risk_records[0].risk_level if fall_risk_records else None
        fall_severity = FALL_RISK_SEVERITY.get(latest_fall_risk, 0.0)

        cutoff = now - timedelta(days=INCIDENT_LOOKBACK_DAYS)
        recent_incidents = [i for i in incidents if _as_aware(i.occurred_at) >= cutoff]
        incident_weight_total = sum(
            INCIDENT_SEVERITY_POINTS.get(i.severity, 0) for i in recent_incidents
        )
        incident_severity = _saturating(incident_weight_total, INCIDENT_SATURATION)

        latest_assistance = assistance_records[0].assistance_level if assistance_records else None
        assistance_severity = ASSISTANCE_SEVERITY.get(latest_assistance, 0.0)

        cognitive_severity = COGNITIVE_STATUS_SEVERITY.get(resident.cognitive_status, 0.0)

        behaviour_cutoff = now - timedelta(days=BEHAVIOUR_LOOKBACK_DAYS)
        recent_behaviour_count = sum(
            1 for b in behaviour_records if _as_aware(b.recorded_at) >= behaviour_cutoff
        )
        behaviour_severity = _saturating(recent_behaviour_count, BEHAVIOUR_SATURATION)


        signals = {
            "fall_risk": (
                fall_severity,
                str(latest_fall_risk) if latest_fall_risk else "No assessment on record",
            ),
            "recent_incidents": (
                incident_severity,
                f"{len(recent_incidents)} incident(s) in last {INCIDENT_LOOKBACK_DAYS} days"
                f" (severity total {incident_weight_total})",
            ),
            "assistance_level": (
                assistance_severity,
                str(latest_assistance) if latest_assistance else "No assessment on record",
            ),
            "cognitive_status": (
                cognitive_severity,
                str(resident.cognitive_status) if resident.cognitive_status else "Unknown",
            ),
            "recent_behaviour": (
                behaviour_severity,
                f"{recent_behaviour_count} event(s) in last {BEHAVIOUR_LOOKBACK_DAYS} days",
            ),
        }

        # SAW: multiply each normalised signal by its weight. Points = 100 x weight x signal,
        # so the points add up to the 0..100 score.
        breakdown: dict[str, RiskScoreBreakdownItem] = {}
        for name, (severity, description) in signals.items():
            weight = RISK_WEIGHTS[name]
            breakdown[name] = RiskScoreBreakdownItem(
                value=description,
                points=round(100 * weight * severity),
                weight=round(weight, 4),
                normalised=round(severity, 4),
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
        scores = await asyncio.gather(*(self.score_resident(r) for r in residents))
        return sorted(scores, key=lambda s: s.score, reverse=True)
