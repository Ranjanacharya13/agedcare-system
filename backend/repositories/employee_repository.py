from supabase import AsyncClient

from backend.models.employee import Employee
from backend.repositories.base import SupabaseRepository


class EmployeeRepository(SupabaseRepository[Employee]):
    def __init__(self, client: AsyncClient):
        super().__init__(client, "employees", Employee)
