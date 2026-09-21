from supabase import AsyncClient

from backend.models.user import User

TABLE_NAME = "users"


class UserRepository:
    def __init__(self, client: AsyncClient):
        self._table = client.table(TABLE_NAME)

    async def create(self, user: User) -> User:
        doc = user.model_dump(mode="json", exclude={"id"})
        response = await self._table.insert(doc).execute()
        return User(**response.data[0])

    async def get_by_id(self, user_id: str) -> User | None:
        response = await self._table.select("*").eq("id", user_id).maybe_single().execute()
        return User(**response.data) if response and response.data else None

    async def get_by_email(self, email: str) -> User | None:
        response = (
            await self._table.select("*").eq("email", email.strip().lower()).maybe_single().execute()
        )
        return User(**response.data) if response and response.data else None

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        response = (
            await self._table.select("*")
            .order("created_at", desc=True)
            .range(skip, skip + limit - 1)
            .execute()
        )
        return [User(**row) for row in response.data]

    async def update(self, user_id: str, updates: dict) -> User | None:
        response = await self._table.update(updates).eq("id", user_id).execute()
        return User(**response.data[0]) if response.data else None

    async def delete(self, user_id: str) -> bool:
        response = await self._table.delete().eq("id", user_id).execute()
        return bool(response.data)
