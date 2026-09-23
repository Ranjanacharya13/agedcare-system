from datetime import datetime

from supabase import AsyncClient

from backend.models.care_visit import ResidentCareVisit
from backend.repositories.base import SupabaseRepository


class CareVisitRepository(SupabaseRepository[ResidentCareVisit]):
    def __init__(self, client: AsyncClient):
        super().__init__(client, "resident_care_visits", ResidentCareVisit, order_column="start_at")

    async def list_between(
        self, start: datetime, end: datetime, employee_id: str | None = None
    ) -> list[ResidentCareVisit]:
        """Visits that intersect [start, end), earliest first."""
        equals = {"employee_id": employee_id} if employee_id else {}
        return await self.list_overlapping("start_at", "end_at", start, end, **equals)
