import asyncio
from datetime import datetime, timedelta, timezone

from supabase import AsyncClient

from backend.services.risk_scoring import RiskScoringService

# There is no real employee<->resident assignment table in this schema, so
# this approximates "which residents has this employee recently cared for"
# by reusing the assessed_by/reported_by/recorded_by/updated_by columns that
# already exist on the resident signal tables -- a schema-free proxy rather
# than a new join table. Expect this to read as (0, 0) for most employees
# today, since those columns are optional and rarely filled in existing test
# data -- it becomes meaningful once real staff usage populates them.
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
    cutoff = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).isoformat()

    async def _fetch(table_name: str, employee_column: str, date_column: str):
        return (
            await client.table(table_name)
            .select("resident_id")
            .eq(employee_column, employee_id)
            .gte(date_column, cutoff)
            .execute()
        )

    # The four signal-table lookups are independent, and so is scoring each
    # distinct resident found -- run both stages concurrently rather than
    # one at a time.
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
