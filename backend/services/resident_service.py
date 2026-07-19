from datetime import datetime, timezone

from fastapi import HTTPException, status

from backend.models.resident import Resident
from backend.repositories.resident_repository import ResidentRepository
from backend.schemas.resident import ResidentCreate, ResidentUpdate


class ResidentService:
    def __init__(self, repository: ResidentRepository):
        self._repository = repository

    async def create_resident(self, data: ResidentCreate) -> Resident:
        resident = Resident(**data.model_dump())
        return await self._repository.create(resident)

    async def get_resident(self, resident_id: str) -> Resident:
        resident = await self._repository.get_by_id(resident_id)
        if resident is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Resident not found")
        return resident

    async def list_residents(self, skip: int = 0, limit: int = 100) -> list[Resident]:
        return await self._repository.list_all(skip, limit)

    async def update_resident(self, resident_id: str, data: ResidentUpdate) -> Resident:
        updates = data.model_dump(mode="json", exclude_unset=True)
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        resident = await self._repository.update(resident_id, updates)
        if resident is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Resident not found")
        return resident

    async def delete_resident(self, resident_id: str) -> None:
        deleted = await self._repository.delete(resident_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Resident not found")
