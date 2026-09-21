from supabase import AsyncClient

from backend.models.complaint import ComplaintFeedback
from backend.repositories.base import SupabaseRepository


class ComplaintRepository(SupabaseRepository[ComplaintFeedback]):
    def __init__(self, client: AsyncClient):
        super().__init__(client, "complaints_feedback", ComplaintFeedback)
