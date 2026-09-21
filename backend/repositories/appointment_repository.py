from supabase import AsyncClient

from backend.models.appointment import Appointment
from backend.repositories.base import SupabaseRepository


class AppointmentRepository(SupabaseRepository[Appointment]):
    def __init__(self, client: AsyncClient):
        super().__init__(client, "appointments", Appointment)
