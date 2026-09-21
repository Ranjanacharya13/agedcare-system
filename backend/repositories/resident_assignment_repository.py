from supabase import AsyncClient

from backend.models.resident_assignment import ResidentAssignment
from backend.repositories.audited import AuditedRepository

TABLE_NAME = "resident_assignments"


class ResidentAssignmentRepository(AuditedRepository):
    """Reads from both sides."""

    def __init__(self, client: AsyncClient):
        self._table = client.table(TABLE_NAME)
        self._audit_table = TABLE_NAME

    async def create(self, assignment: ResidentAssignment) -> ResidentAssignment:
        doc = assignment.model_dump(mode="json", exclude={"id"})
        response = await self._table.insert(doc).execute()
        created = ResidentAssignment(**response.data[0])
        await self._audit_create(created)
        return created

    async def get_by_id(self, assignment_id: str) -> ResidentAssignment | None:
        response = await self._table.select("*").eq("id", assignment_id).maybe_single().execute()
        return ResidentAssignment(**response.data) if response and response.data else None

    async def list_for_resident(
        self, resident_id: str, *, active_only: bool = False
    ) -> list[ResidentAssignment]:
        query = self._table.select("*").eq("resident_id", resident_id)
        if active_only:
            query = query.eq("active", True)
        response = await query.execute()
        return [ResidentAssignment(**row) for row in response.data]

    async def list_for_employee(
        self, employee_id: str, *, active_only: bool = False
    ) -> list[ResidentAssignment]:
        query = self._table.select("*").eq("employee_id", employee_id)
        if active_only:
            query = query.eq("active", True)
        response = await query.execute()
        return [ResidentAssignment(**row) for row in response.data]

    async def list_all(
        self, skip: int = 0, limit: int = 1000, *, active_only: bool = False
    ) -> list[ResidentAssignment]:
        query = self._table.select("*")
        if active_only:
            query = query.eq("active", True)
        response = await query.range(skip, skip + limit - 1).execute()
        return [ResidentAssignment(**row) for row in response.data]

    async def update(self, assignment_id: str, updates: dict) -> ResidentAssignment | None:
        before = await self.get_by_id(assignment_id)
        response = await self._table.update(updates).eq("id", assignment_id).execute()
        if not response.data:
            return None
        updated = ResidentAssignment(**response.data[0])
        await self._audit_update(assignment_id, before, updated)
        return updated

    async def delete(self, assignment_id: str) -> bool:
        before = await self.get_by_id(assignment_id)
        response = await self._table.delete().eq("id", assignment_id).execute()
        deleted = bool(response.data)
        if deleted:
            await self._audit_delete(assignment_id, before)
        return deleted
