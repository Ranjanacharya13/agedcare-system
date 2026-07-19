from fastapi import HTTPException, status

from backend.models.medical_history import ResidentMedicalHistory
from backend.repositories.medical_history_repository import MedicalHistoryRepository
from backend.repositories.resident_repository import ResidentRepository
from backend.schemas.medical_history import MedicalHistoryCreate, MedicalHistoryUpdate


class MedicalHistoryService:
    def __init__(
        self,
        repository: MedicalHistoryRepository,
        resident_repository: ResidentRepository,
    ):
        self._repository = repository
        self._resident_repository = resident_repository

    async def _ensure_resident_exists(self, resident_id: str) -> None:
        resident = await self._resident_repository.get_by_id(resident_id)
        if resident is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Resident not found")

    async def create_record(
        self, resident_id: str, data: MedicalHistoryCreate
    ) -> ResidentMedicalHistory:
        await self._ensure_resident_exists(resident_id)
        record = ResidentMedicalHistory(resident_id=resident_id, **data.model_dump())
        return await self._repository.create(record)

    async def get_record(self, resident_id: str, record_id: str) -> ResidentMedicalHistory:
        record = await self._repository.get_by_id(record_id)
        if record is None or str(record.resident_id) != resident_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medical history record not found")
        return record

    async def list_records(
        self, resident_id: str, skip: int = 0, limit: int = 100
    ) -> list[ResidentMedicalHistory]:
        await self._ensure_resident_exists(resident_id)
        return await self._repository.list_for_resident(resident_id, skip, limit)

    async def list_all_records(
        self, skip: int = 0, limit: int = 100
    ) -> list[ResidentMedicalHistory]:
        return await self._repository.list_all(skip, limit)

    async def update_record(
        self, resident_id: str, record_id: str, data: MedicalHistoryUpdate
    ) -> ResidentMedicalHistory:
        await self.get_record(resident_id, record_id)
        updates = data.model_dump(exclude_unset=True)
        record = await self._repository.update(record_id, updates)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medical history record not found")
        return record

    async def delete_record(self, resident_id: str, record_id: str) -> None:
        await self.get_record(resident_id, record_id)
        deleted = await self._repository.delete(record_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medical history record not found")
