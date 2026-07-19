from typing import Annotated, Callable

from fastapi import APIRouter, Depends, Path, status
from pydantic import BaseModel

from backend.services.base import ParentScopedService


def build_parent_scoped_routers(
    *,
    parent_param: str,
    create_schema: type[BaseModel],
    update_schema: type[BaseModel],
    out_schema: type[BaseModel],
    get_service: Callable[..., ParentScopedService],
) -> tuple[APIRouter, APIRouter]:
    router = APIRouter()
    all_router = APIRouter()

    @all_router.get("", response_model=list[out_schema])
    async def list_all(
        skip: int = 0, limit: int = 100, service: ParentScopedService = Depends(get_service)
    ):
        return await service.list_all_records(skip, limit)

    @router.post("", response_model=out_schema, status_code=status.HTTP_201_CREATED)
    async def create(
        *,
        parent_id: Annotated[str, Path(alias=parent_param)],
        data: create_schema,
        service: ParentScopedService = Depends(get_service),
    ):
        return await service.create_record(parent_id, data)

    @router.get("", response_model=list[out_schema])
    async def list_for_parent(
        *,
        parent_id: Annotated[str, Path(alias=parent_param)],
        skip: int = 0,
        limit: int = 100,
        service: ParentScopedService = Depends(get_service),
    ):
        return await service.list_records(parent_id, skip, limit)

    @router.get("/{record_id}", response_model=out_schema)
    async def get_one(
        *,
        parent_id: Annotated[str, Path(alias=parent_param)],
        record_id: str,
        service: ParentScopedService = Depends(get_service),
    ):
        return await service.get_record(parent_id, record_id)

    @router.patch("/{record_id}", response_model=out_schema)
    async def update(
        *,
        parent_id: Annotated[str, Path(alias=parent_param)],
        record_id: str,
        data: update_schema,
        service: ParentScopedService = Depends(get_service),
    ):
        return await service.update_record(parent_id, record_id, data)

    @router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete(
        *,
        parent_id: Annotated[str, Path(alias=parent_param)],
        record_id: str,
        service: ParentScopedService = Depends(get_service),
    ):
        await service.delete_record(parent_id, record_id)

    return router, all_router
