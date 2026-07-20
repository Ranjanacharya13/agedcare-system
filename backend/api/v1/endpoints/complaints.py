from fastapi import APIRouter, Depends, status

from backend.api.deps import get_complaint_service
from backend.schemas.complaint import ComplaintCreate, ComplaintOut, ComplaintUpdate
from backend.services.complaint_service import ComplaintService

router = APIRouter()


@router.post("", response_model=ComplaintOut, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    data: ComplaintCreate, service: ComplaintService = Depends(get_complaint_service)
):
    return await service.create_complaint(data)


@router.get("", response_model=list[ComplaintOut])
async def list_complaints(
    skip: int = 0, limit: int = 100, service: ComplaintService = Depends(get_complaint_service)
):
    return await service.list_complaints(skip, limit)


@router.get("/{complaint_id}", response_model=ComplaintOut)
async def get_complaint(
    complaint_id: str, service: ComplaintService = Depends(get_complaint_service)
):
    return await service.get_complaint(complaint_id)


@router.patch("/{complaint_id}", response_model=ComplaintOut)
async def update_complaint(
    complaint_id: str,
    data: ComplaintUpdate,
    service: ComplaintService = Depends(get_complaint_service),
):
    return await service.update_complaint(complaint_id, data)


@router.delete("/{complaint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_complaint(
    complaint_id: str, service: ComplaintService = Depends(get_complaint_service)
):
    await service.delete_complaint(complaint_id)
