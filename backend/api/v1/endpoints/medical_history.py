from fastapi import APIRouter, Depends, status

from backend.api.deps import get_medical_history_service
from backend.schemas.medical_history import (
    MedicalHistoryCreate,
    MedicalHistoryOut,
    MedicalHistoryUpdate,
)
from backend.services.medical_history_service import MedicalHistoryService

router = APIRouter()
all_router = APIRouter()


@all_router.get("", response_model=list[MedicalHistoryOut])
async def list_all_medical_history(
    skip: int = 0,
    limit: int = 100,
    service: MedicalHistoryService = Depends(get_medical_history_service),
):
    return await service.list_all_records(skip, limit)


@router.post("", response_model=MedicalHistoryOut, status_code=status.HTTP_201_CREATED)
async def create_medical_history(
    resident_id: str,
    data: MedicalHistoryCreate,
    service: MedicalHistoryService = Depends(get_medical_history_service),
):
    return await service.create_record(resident_id, data)


@router.get("", response_model=list[MedicalHistoryOut])
async def list_medical_history(
    resident_id: str,
    skip: int = 0,
    limit: int = 100,
    service: MedicalHistoryService = Depends(get_medical_history_service),
):
    return await service.list_records(resident_id, skip, limit)


@router.get("/{record_id}", response_model=MedicalHistoryOut)
async def get_medical_history(
    resident_id: str,
    record_id: str,
    service: MedicalHistoryService = Depends(get_medical_history_service),
):
    return await service.get_record(resident_id, record_id)


@router.patch("/{record_id}", response_model=MedicalHistoryOut)
async def update_medical_history(
    resident_id: str,
    record_id: str,
    data: MedicalHistoryUpdate,
    service: MedicalHistoryService = Depends(get_medical_history_service),
):
    return await service.update_record(resident_id, record_id, data)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medical_history(
    resident_id: str,
    record_id: str,
    service: MedicalHistoryService = Depends(get_medical_history_service),
):
    await service.delete_record(resident_id, record_id)
