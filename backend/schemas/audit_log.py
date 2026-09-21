from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from backend.models.audit_log import AuditAction


class AuditLogOut(BaseModel):
    id: UUID
    action: AuditAction
    table_name: str
    record_id: str | None = None
    actor_id: UUID | None = None
    actor_email: str | None = None
    actor_role: str | None = None
    request_id: str | None = None
    ip_address: str | None = None
    changes: dict | None = None
    detail: str | None = None
    created_at: datetime
