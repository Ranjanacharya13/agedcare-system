from typing import Generic, Protocol, TypeVar

from fastapi import HTTPException, status
from pydantic import BaseModel

from backend.repositories.base import SupabaseRepository

ModelT = TypeVar("ModelT", bound=BaseModel)


class ParentRepository(Protocol):
    async def get_by_id(self, record_id: str) -> object | None: ...


class ParentScopedService(Generic[ModelT]):
    def __init__(
        self,
        repository: SupabaseRepository[ModelT],
        parent_repository: ParentRepository,
        model: type[ModelT],
        parent_field: str,
        not_found_message: str,
        parent_not_found_message: str = "Parent record not found",
    ):
        self._repository = repository
        self._parent_repository = parent_repository
        self._model = model
        self._parent_field = parent_field
        self._not_found_message = not_found_message
        self._parent_not_found_message = parent_not_found_message

    async def _ensure_parent_exists(self, parent_id: str) -> None:
        parent = await self._parent_repository.get_by_id(parent_id)
        if parent is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, self._parent_not_found_message)

    async def create_record(self, parent_id: str, data: BaseModel) -> ModelT:
        await self._ensure_parent_exists(parent_id)
        record = self._model(**{self._parent_field: parent_id}, **data.model_dump())
        return await self._repository.create(record)

    async def get_record(self, parent_id: str, record_id: str) -> ModelT:
        record = await self._repository.get_by_id(record_id)
        if record is None or str(getattr(record, self._parent_field)) != parent_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, self._not_found_message)
        return record

    async def list_records(self, parent_id: str, skip: int = 0, limit: int = 100) -> list[ModelT]:
        await self._ensure_parent_exists(parent_id)
        return await self._repository.list_for_parent(parent_id, skip, limit)

    async def list_all_records(self, skip: int = 0, limit: int = 100) -> list[ModelT]:
        return await self._repository.list_all(skip, limit)

    async def update_record(self, parent_id: str, record_id: str, data: BaseModel) -> ModelT:
        await self.get_record(parent_id, record_id)
        updates = data.model_dump(mode="json", exclude_unset=True)
        record = await self._repository.update(record_id, updates)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, self._not_found_message)
        return record

    async def delete_record(self, parent_id: str, record_id: str) -> None:
        await self.get_record(parent_id, record_id)
        deleted = await self._repository.delete(record_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, self._not_found_message)
