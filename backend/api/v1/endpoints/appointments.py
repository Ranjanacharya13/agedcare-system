from fastapi import APIRouter, Depends, status

from backend.api.deps import get_appointment_service
from backend.schemas.appointment import AppointmentCreate, AppointmentOut, AppointmentUpdate
from backend.services.base import CrudService

router = APIRouter()


@router.post("", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    data: AppointmentCreate, service: CrudService = Depends(get_appointment_service)
):
    return await service.create(data)


@router.get("", response_model=list[AppointmentOut])
async def list_appointments(
    skip: int = 0, limit: int = 100, service: CrudService = Depends(get_appointment_service)
):
    return await service.list(skip, limit)


@router.get("/{appointment_id}", response_model=AppointmentOut)
async def get_appointment(
    appointment_id: str, service: CrudService = Depends(get_appointment_service)
):
    return await service.get(appointment_id)


@router.patch("/{appointment_id}", response_model=AppointmentOut)
async def update_appointment(
    appointment_id: str,
    data: AppointmentUpdate,
    service: CrudService = Depends(get_appointment_service),
):
    return await service.update(appointment_id, data)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: str, service: CrudService = Depends(get_appointment_service)
):
    await service.delete(appointment_id)
