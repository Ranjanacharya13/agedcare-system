"""Audit hooks shared by every repository."""

from typing import Any

from pydantic import BaseModel

from backend.models.audit_log import AuditAction
from backend.services import audit


def _as_dict(record: Any) -> dict | None:
    if record is None:
        return None
    if isinstance(record, BaseModel):
        return record.model_dump(mode="json")
    if isinstance(record, dict):
        return record
    return None


class AuditedRepository:
    """Mixin."""

    _audit_table: str = "unknown"

    async def _audit_create(self, created: Any) -> None:
        after = _as_dict(created)
        await audit.record_data_change(
            action=AuditAction.CREATE,
            table_name=self._audit_table,
            record_id=str(after.get("id")) if after else None,
            after=after,
        )

    async def _audit_update(self, record_id: str, before: Any, after: Any) -> None:
        await audit.record_data_change(
            action=AuditAction.UPDATE,
            table_name=self._audit_table,
            record_id=str(record_id),
            before=_as_dict(before),
            after=_as_dict(after),
        )

    async def _audit_delete(self, record_id: str, before: Any) -> None:
        await audit.record_data_change(
            action=AuditAction.DELETE,
            table_name=self._audit_table,
            record_id=str(record_id),
            before=_as_dict(before),
        )
