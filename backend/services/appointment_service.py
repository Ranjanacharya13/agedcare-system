from datetime import datetime, timezone

from fastapi import HTTPException, status

from backend.models.appointment import Appointment
from backend.repositories.appointment_repository import AppointmentRepository
from backend.schemas.appointment import AppointmentCreate, AppointmentUpdate


class AppointmentService:
    def __init__(self, repository: AppointmentRepository):
        self._repository = repository

    async def create_appointment(self, data: AppointmentCreate) -> Appointment:
        appointment = Appointment(**data.model_dump())
        return await self._repository.create(appointment)

    async def get_appointment(self, appointment_id: str) -> Appointment:
        appointment = await self._repository.get_by_id(appointment_id)
        if appointment is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Appointment not found")
        return appointment

    async def list_appointments(self, skip: int = 0, limit: int = 100) -> list[Appointment]:
        return await self._repository.list_all(skip, limit)

    async def update_appointment(self, appointment_id: str, data: AppointmentUpdate) -> Appointment:
        updates = data.model_dump(mode="json", exclude_unset=True)
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        appointment = await self._repository.update(appointment_id, updates)
        if appointment is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Appointment not found")
        return appointment

    async def delete_appointment(self, appointment_id: str) -> None:
        deleted = await self._repository.delete(appointment_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Appointment not found")
