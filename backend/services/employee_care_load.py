import asyncio
from datetime import datetime, timedelta, timezone

from supabase import AsyncClient

from backend.services.risk_scoring import RiskScoringService

CARE_LOAD_LOOKBACK_DAYS = 30

_SIGNAL_TABLES = (
    ("resident_fall_risk", "assessed_by", "assessment_date"),
    ("resident_incidents", "reported_by", "occurred_at"),
    ("resident_behaviour", "recorded_by", "recorded_at"),
    ("resident_assistance", "updated_by", "updated_at"),
)


async def get_employee_care_load(
    employee_id: str,
    client: AsyncClient,
    risk_scoring_service: RiskScoringService,
    lookback_days: int = CARE_LOAD_LOOKBACK_DAYS,
) -> tuple[float, int]:
    """Returns (care load, residents cared for). Care load = sum of the risk scores of the
    residents this employee recently recorded something for, so riskier residents weigh more
    than a plain head count. Callers normalise it (a SAW cost criterion) when comparing staff.
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).isoformat()

    async def _fetch(table_name: str, employee_column: str, date_column: str):
        return (
            await client.table(table_name)
            .select("resident_id")
            .eq(employee_column, employee_id)
            .gte(date_column, cutoff)
            .execute()
        )

    responses = await asyncio.gather(*(_fetch(*table) for table in _SIGNAL_TABLES))
    resident_ids: set[str] = set()
    for response in responses:
        resident_ids.update(row["resident_id"] for row in response.data)

    if not resident_ids:
        return 0.0, 0

    results = await asyncio.gather(
        *(risk_scoring_service.get_resident_score(resident_id) for resident_id in resident_ids)
    )
    scores = [result.score for result in results if result is not None]
    return float(sum(scores)), len(resident_ids)
