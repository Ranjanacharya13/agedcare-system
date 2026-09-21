from supabase import AsyncClient

from backend.models.audit_log import AuditLog

TABLE_NAME = "audit_log"


class AuditRepository:
    """Insert and read only — there is deliberately no update or delete."""

    def __init__(self, client: AsyncClient):
        self._table = client.table(TABLE_NAME)

    async def create(self, entry: AuditLog) -> AuditLog:
        doc = entry.model_dump(mode="json", exclude={"id"})
        response = await self._table.insert(doc).execute()
        return AuditLog(**response.data[0])

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[AuditLog]:
        response = (
            await self._table.select("*")
            .order("created_at", desc=True)
            .range(skip, skip + limit - 1)
            .execute()
        )
        return [AuditLog(**row) for row in response.data]

    async def list_for_record(
        self, table_name: str, record_id: str, skip: int = 0, limit: int = 100
    ) -> list[AuditLog]:
        response = (
            await self._table.select("*")
            .eq("table_name", table_name)
            .eq("record_id", record_id)
            .order("created_at", desc=True)
            .range(skip, skip + limit - 1)
            .execute()
        )
        return [AuditLog(**row) for row in response.data]
