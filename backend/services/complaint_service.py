from datetime import datetime, timezone

from fastapi import HTTPException, status

from backend.models.complaint import ComplaintFeedback
from backend.repositories.complaint_repository import ComplaintRepository
from backend.schemas.complaint import ComplaintCreate, ComplaintUpdate


class ComplaintService:
    def __init__(self, repository: ComplaintRepository):
        self._repository = repository

    async def create_complaint(self, data: ComplaintCreate) -> ComplaintFeedback:
        complaint = ComplaintFeedback(**data.model_dump())
        return await self._repository.create(complaint)

    async def get_complaint(self, complaint_id: str) -> ComplaintFeedback:
        complaint = await self._repository.get_by_id(complaint_id)
        if complaint is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Complaint not found")
        return complaint

    async def list_complaints(self, skip: int = 0, limit: int = 100) -> list[ComplaintFeedback]:
        return await self._repository.list_all(skip, limit)

    async def update_complaint(self, complaint_id: str, data: ComplaintUpdate) -> ComplaintFeedback:
        updates = data.model_dump(mode="json", exclude_unset=True)
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        complaint = await self._repository.update(complaint_id, updates)
        if complaint is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Complaint not found")
        return complaint

    async def delete_complaint(self, complaint_id: str) -> None:
        deleted = await self._repository.delete(complaint_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Complaint not found")
