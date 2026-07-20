from supabase import AsyncClient

from backend.models.complaint import ComplaintFeedback

TABLE_NAME = "complaints_feedback"


class ComplaintRepository:
    def __init__(self, client: AsyncClient):
        self._table = client.table(TABLE_NAME)

    async def create(self, complaint: ComplaintFeedback) -> ComplaintFeedback:
        doc = complaint.model_dump(mode="json", exclude={"id"})
        response = await self._table.insert(doc).execute()
        return ComplaintFeedback(**response.data[0])

    async def get_by_id(self, complaint_id: str) -> ComplaintFeedback | None:
        response = await self._table.select("*").eq("id", complaint_id).maybe_single().execute()
        return ComplaintFeedback(**response.data) if response and response.data else None

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[ComplaintFeedback]:
        response = await self._table.select("*").range(skip, skip + limit - 1).execute()
        return [ComplaintFeedback(**row) for row in response.data]

    async def update(self, complaint_id: str, updates: dict) -> ComplaintFeedback | None:
        response = await self._table.update(updates).eq("id", complaint_id).execute()
        return ComplaintFeedback(**response.data[0]) if response.data else None

    async def delete(self, complaint_id: str) -> bool:
        response = await self._table.delete().eq("id", complaint_id).execute()
        return bool(response.data)
