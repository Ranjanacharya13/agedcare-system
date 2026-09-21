"""Audit recording."""

import logging
from typing import Any

from backend.core.request_context import get_actor, get_ip_address, get_request_id
from backend.db.supabase_client import get_supabase
from backend.models.audit_log import AuditAction, AuditLog
from backend.repositories.audit_repository import AuditRepository

logger = logging.getLogger(__name__)

#: Never write these values into the audit log, whatever table they come from.
SENSITIVE_FIELDS = frozenset({"password", "password_hash", "token", "access_token", "secret"})

_REDACTED = "***redacted***"


def _redact(value: Any, field: str) -> Any:
    return _REDACTED if field.lower() in SENSITIVE_FIELDS else value


def diff_changes(before: dict | None, after: dict | None) -> dict:
    before = before or {}
    after = after or {}
    changes: dict[str, dict[str, Any]] = {}
    for field in set(before) | set(after):
        old = before.get(field)
        new = after.get(field)
        if old == new:
            continue
        changes[field] = {"from": _redact(old, field), "to": _redact(new, field)}
    return changes


async def _write(entry: AuditLog) -> None:
    try:
        repository = AuditRepository(get_supabase())
        await repository.create(entry)
    except Exception:  # noqa: BLE001 - audit must never break the request
        logger.exception("Failed to write audit entry for %s/%s", entry.table_name, entry.record_id)


async def record_data_change(
    *,
    action: AuditAction,
    table_name: str,
    record_id: str | None,
    before: dict | None = None,
    after: dict | None = None,
    detail: str | None = None,
) -> None:
    actor = get_actor()
    changes = diff_changes(before, after)
    if action == AuditAction.UPDATE and not changes:
        # A PATCH that changed nothing is noise, not history.
        return
    await _write(
        AuditLog(
            action=action,
            table_name=table_name,
            record_id=str(record_id) if record_id is not None else None,
            actor_id=actor.id,
            actor_email=actor.email,
            actor_role=actor.role,
            request_id=get_request_id(),
            ip_address=get_ip_address(),
            changes=changes or None,
            detail=detail,
        )
    )


async def record_event(
    *,
    action: AuditAction,
    table_name: str = "auth",
    record_id: str | None = None,
    detail: str | None = None,
    actor_email: str | None = None,
) -> None:
    actor = get_actor()
    await _write(
        AuditLog(
            action=action,
            table_name=table_name,
            record_id=str(record_id) if record_id is not None else None,
            actor_id=actor.id,
            actor_email=actor.email or actor_email,
            actor_role=actor.role,
            request_id=get_request_id(),
            ip_address=get_ip_address(),
            detail=detail,
        )
    )
