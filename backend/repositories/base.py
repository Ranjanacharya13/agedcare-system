from typing import Generic, TypeVar

from pydantic import BaseModel
from supabase import AsyncClient

from backend.repositories.audited import AuditedRepository

ModelT = TypeVar("ModelT", bound=BaseModel)


class SupabaseRepository(AuditedRepository, Generic[ModelT]):
    def __init__(
        self,
        client: AsyncClient,
        table_name: str,
        model: type[ModelT],
        order_column: str | None = None,
        parent_field: str = "resident_id",
    ):
        self._table = client.table(table_name)
        self._audit_table = table_name
        self._model = model
        self._order_column = order_column
        self._parent_field = parent_field

    def _ordered(self, query):
        if self._order_column:
            return query.order(self._order_column, desc=True)
        return query

    async def create(self, record: ModelT) -> ModelT:
        doc = record.model_dump(mode="json", exclude={"id"})
        response = await self._table.insert(doc).execute()
        created = self._model(**response.data[0])
        await self._audit_create(created)
        return created

    async def get_by_id(self, record_id: str) -> ModelT | None:
        response = await self._table.select("*").eq("id", record_id).maybe_single().execute()
        return self._model(**response.data) if response and response.data else None

    async def list_for_parent(
        self, parent_id: str, skip: int = 0, limit: int = 100
    ) -> list[ModelT]:
        query = self._ordered(self._table.select("*").eq(self._parent_field, parent_id))
        response = await query.range(skip, skip + limit - 1).execute()
        return [self._model(**row) for row in response.data]

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[ModelT]:
        query = self._ordered(self._table.select("*"))
        response = await query.range(skip, skip + limit - 1).execute()
        return [self._model(**row) for row in response.data]

    async def list_overlapping(
        self, start_field: str, end_field: str, start, end, **equals
    ) -> list[ModelT]:
        """Rows whose [start_field, end_field) intersects [start, end), earliest first."""
        query = (
            self._table.select("*")
            .lt(start_field, end.isoformat())
            .gt(end_field, start.isoformat())
        )
        for field, value in equals.items():
            query = query.eq(field, value)
        response = await query.order(start_field).execute()
        return [self._model(**row) for row in response.data]

    async def update(self, record_id: str, updates: dict) -> ModelT | None:
        before = await self.get_by_id(record_id)
        response = await self._table.update(updates).eq("id", record_id).execute()
        if not response.data:
            return None
        updated = self._model(**response.data[0])
        await self._audit_update(record_id, before, updated)
        return updated

    async def delete(self, record_id: str) -> bool:
        before = await self.get_by_id(record_id)
        response = await self._table.delete().eq("id", record_id).execute()
        deleted = bool(response.data)
        if deleted:
            await self._audit_delete(record_id, before)
        return deleted
