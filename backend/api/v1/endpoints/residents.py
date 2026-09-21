from fastapi import APIRouter, Depends, status

from backend.api.deps import get_resident_service
from backend.schemas.resident import ResidentCreate, ResidentOut, ResidentUpdate
from backend.services.base import CrudService

router = APIRouter()


@router.post("", response_model=ResidentOut, status_code=status.HTTP_201_CREATED)
async def create_resident(
    data: ResidentCreate, service: CrudService = Depends(get_resident_service)
):
    return await service.create(data)


@router.get("", response_model=list[ResidentOut])
async def list_residents(
    skip: int = 0, limit: int = 100, service: CrudService = Depends(get_resident_service)
):
    return await service.list(skip, limit)


@router.get("/{resident_id}", response_model=ResidentOut)
async def get_resident(
    resident_id: str, service: CrudService = Depends(get_resident_service)
):
    return await service.get(resident_id)


@router.patch("/{resident_id}", response_model=ResidentOut)
async def update_resident(
    resident_id: str,
    data: ResidentUpdate,
    service: CrudService = Depends(get_resident_service),
):
    return await service.update(resident_id, data)


@router.delete("/{resident_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resident(
    resident_id: str, service: CrudService = Depends(get_resident_service)
):
    await service.delete(resident_id)
