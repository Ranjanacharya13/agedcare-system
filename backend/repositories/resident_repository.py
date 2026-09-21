from supabase import AsyncClient

from backend.models.resident import Resident
from backend.repositories.base import SupabaseRepository


class ResidentRepository(SupabaseRepository[Resident]):
    def __init__(self, client: AsyncClient):
        super().__init__(client, "residents", Resident)
