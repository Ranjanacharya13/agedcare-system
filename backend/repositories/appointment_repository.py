from supabase import AsyncClient

from backend.models.appointment import Appointment

TABLE_NAME = "appointments"


class AppointmentRepository:
    def __init__(self, client: AsyncClient):
        self._table = client.table(TABLE_NAME)

    async def create(self, appointment: Appointment) -> Appointment:
        doc = appointment.model_dump(mode="json", exclude={"id"})
        response = await self._table.insert(doc).execute()
        return Appointment(**response.data[0])

    async def get_by_id(self, appointment_id: str) -> Appointment | None:
        response = await self._table.select("*").eq("id", appointment_id).maybe_single().execute()
        return Appointment(**response.data) if response and response.data else None

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Appointment]:
        response = await self._table.select("*").range(skip, skip + limit - 1).execute()
        return [Appointment(**row) for row in response.data]

    async def update(self, appointment_id: str, updates: dict) -> Appointment | None:
        response = await self._table.update(updates).eq("id", appointment_id).execute()
        return Appointment(**response.data[0]) if response.data else None

    async def delete(self, appointment_id: str) -> bool:
        response = await self._table.delete().eq("id", appointment_id).execute()
        return bool(response.data)
