from fastapi import APIRouter, Depends

from backend.api.deps import get_audit_repository
from backend.repositories.audit_repository import AuditRepository
from backend.schemas.audit_log import AuditLogOut

router = APIRouter()


@router.get("", response_model=list[AuditLogOut])
async def list_audit_log(
    skip: int = 0,
    limit: int = 100,
    repository: AuditRepository = Depends(get_audit_repository),
):
    return await repository.list_all(skip, limit)


@router.get("/{table_name}/{record_id}", response_model=list[AuditLogOut])
async def list_audit_log_for_record(
    table_name: str,
    record_id: str,
    skip: int = 0,
    limit: int = 100,
    repository: AuditRepository = Depends(get_audit_repository),
):
    return await repository.list_for_record(table_name, record_id, skip, limit)
