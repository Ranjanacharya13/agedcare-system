from supabase import AsyncClient

from backend.models.medical_history import ResidentMedicalHistory

TABLE_NAME = "resident_medical_history"


class MedicalHistoryRepository:
    def __init__(self, client: AsyncClient):
        self._table = client.table(TABLE_NAME)

    async def create(self, record: ResidentMedicalHistory) -> ResidentMedicalHistory:
        doc = record.model_dump(mode="json", exclude={"id"})
        response = await self._table.insert(doc).execute()
        return ResidentMedicalHistory(**response.data[0])

    async def get_by_id(self, record_id: str) -> ResidentMedicalHistory | None:
        response = await self._table.select("*").eq("id", record_id).maybe_single().execute()
        return ResidentMedicalHistory(**response.data) if response and response.data else None

    async def list_for_resident(
        self, resident_id: str, skip: int = 0, limit: int = 100
    ) -> list[ResidentMedicalHistory]:
        response = (
            await self._table.select("*")
            .eq("resident_id", resident_id)
            .order("recorded_at", desc=True)
            .range(skip, skip + limit - 1)
            .execute()
        )
        return [ResidentMedicalHistory(**row) for row in response.data]

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[ResidentMedicalHistory]:
        response = (
            await self._table.select("*")
            .order("recorded_at", desc=True)
            .range(skip, skip + limit - 1)
            .execute()
        )
        return [ResidentMedicalHistory(**row) for row in response.data]

    async def update(self, record_id: str, updates: dict) -> ResidentMedicalHistory | None:
        response = await self._table.update(updates).eq("id", record_id).execute()
        return ResidentMedicalHistory(**response.data[0]) if response.data else None

    async def delete(self, record_id: str) -> bool:
        response = await self._table.delete().eq("id", record_id).execute()
        return bool(response.data)
