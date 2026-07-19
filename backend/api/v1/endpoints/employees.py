from fastapi import APIRouter, Depends, status

from backend.api.deps import get_employee_service
from backend.schemas.employee import EmployeeCreate, EmployeeOut, EmployeeUpdate
from backend.services.employee_service import EmployeeService

router = APIRouter()


@router.post("", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
async def create_employee(
    data: EmployeeCreate, service: EmployeeService = Depends(get_employee_service)
):
    return await service.create_employee(data)


@router.get("", response_model=list[EmployeeOut])
async def list_employees(
    skip: int = 0, limit: int = 100, service: EmployeeService = Depends(get_employee_service)
):
    return await service.list_employees(skip, limit)


@router.get("/{employee_id}", response_model=EmployeeOut)
async def get_employee(
    employee_id: str, service: EmployeeService = Depends(get_employee_service)
):
    return await service.get_employee(employee_id)


@router.patch("/{employee_id}", response_model=EmployeeOut)
async def update_employee(
    employee_id: str,
    data: EmployeeUpdate,
    service: EmployeeService = Depends(get_employee_service),
):
    return await service.update_employee(employee_id, data)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: str, service: EmployeeService = Depends(get_employee_service)
):
    await service.delete_employee(employee_id)
