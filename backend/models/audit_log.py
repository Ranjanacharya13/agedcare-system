from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class AuditAction(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    ACCESS_DENIED = "access_denied"


class AuditLog(BaseModel):
    """One immutable row per meaningful change."""

    id: UUID | None = None
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
