from supabase import AsyncClient

from backend.models.resident import Resident

TABLE_NAME = "residents"


class ResidentRepository:
    def __init__(self, client: AsyncClient):
        self._table = client.table(TABLE_NAME)

    async def create(self, resident: Resident) -> Resident:
        doc = resident.model_dump(mode="json", exclude={"id"})
        response = await self._table.insert(doc).execute()
        return Resident(**response.data[0])

    async def get_by_id(self, resident_id: str) -> Resident | None:
        response = await self._table.select("*").eq("id", resident_id).maybe_single().execute()
        return Resident(**response.data) if response and response.data else None

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Resident]:
        response = (
            await self._table.select("*").range(skip, skip + limit - 1).execute()
        )
        return [Resident(**row) for row in response.data]

    async def update(self, resident_id: str, updates: dict) -> Resident | None:
        response = await self._table.update(updates).eq("id", resident_id).execute()
        return Resident(**response.data[0]) if response.data else None

    async def delete(self, resident_id: str) -> bool:
        response = await self._table.delete().eq("id", resident_id).execute()
        return bool(response.data)
