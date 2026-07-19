from datetime import datetime, timezone

from fastapi import HTTPException, status

from backend.models.employee import Employee
from backend.repositories.employee_repository import EmployeeRepository
from backend.schemas.employee import EmployeeCreate, EmployeeUpdate


class EmployeeService:
    def __init__(self, repository: EmployeeRepository):
        self._repository = repository

    async def create_employee(self, data: EmployeeCreate) -> Employee:
        employee = Employee(**data.model_dump())
        return await self._repository.create(employee)

    async def get_employee(self, employee_id: str) -> Employee:
        employee = await self._repository.get_by_id(employee_id)
        if employee is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")
        return employee

    async def list_employees(self, skip: int = 0, limit: int = 100) -> list[Employee]:
        return await self._repository.list_all(skip, limit)

    async def update_employee(self, employee_id: str, data: EmployeeUpdate) -> Employee:
        updates = data.model_dump(mode="json", exclude_unset=True)
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        employee = await self._repository.update(employee_id, updates)
        if employee is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")
        return employee

    async def delete_employee(self, employee_id: str) -> None:
        deleted = await self._repository.delete(employee_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")
