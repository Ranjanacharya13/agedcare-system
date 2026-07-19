from supabase import AsyncClient

from backend.models.employee import Employee

TABLE_NAME = "employees"


class EmployeeRepository:
    def __init__(self, client: AsyncClient):
        self._table = client.table(TABLE_NAME)

    async def create(self, employee: Employee) -> Employee:
        doc = employee.model_dump(mode="json", exclude={"id"})
        response = await self._table.insert(doc).execute()
        return Employee(**response.data[0])

    async def get_by_id(self, employee_id: str) -> Employee | None:
        response = await self._table.select("*").eq("id", employee_id).maybe_single().execute()
        return Employee(**response.data) if response and response.data else None

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Employee]:
        response = await self._table.select("*").range(skip, skip + limit - 1).execute()
        return [Employee(**row) for row in response.data]

    async def update(self, employee_id: str, updates: dict) -> Employee | None:
        response = await self._table.update(updates).eq("id", employee_id).execute()
        return Employee(**response.data[0]) if response.data else None

    async def delete(self, employee_id: str) -> bool:
        response = await self._table.delete().eq("id", employee_id).execute()
        return bool(response.data)
