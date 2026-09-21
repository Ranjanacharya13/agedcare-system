from fastapi import APIRouter, Depends, status

from backend.api.deps import get_complaint_service
from backend.schemas.complaint import ComplaintCreate, ComplaintOut, ComplaintUpdate
from backend.services.base import CrudService

router = APIRouter()


@router.post("", response_model=ComplaintOut, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    data: ComplaintCreate, service: CrudService = Depends(get_complaint_service)
):
    return await service.create(data)


@router.get("", response_model=list[ComplaintOut])
async def list_complaints(
    skip: int = 0, limit: int = 100, service: CrudService = Depends(get_complaint_service)
):
    return await service.list(skip, limit)


@router.get("/{complaint_id}", response_model=ComplaintOut)
async def get_complaint(
    complaint_id: str, service: CrudService = Depends(get_complaint_service)
):
    return await service.get(complaint_id)


@router.patch("/{complaint_id}", response_model=ComplaintOut)
async def update_complaint(
    complaint_id: str,
    data: ComplaintUpdate,
    service: CrudService = Depends(get_complaint_service),
):
    return await service.update(complaint_id, data)


@router.delete("/{complaint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_complaint(
    complaint_id: str, service: CrudService = Depends(get_complaint_service)
):
    await service.delete(complaint_id)
