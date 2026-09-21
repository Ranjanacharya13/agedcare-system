"""Authentication and authorisation dependencies."""

from typing import Annotated, Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.config.permissions import action_for_method, can, roles_for
from backend.config.security import TokenError, decode_access_token
from backend.core.request_context import Actor, set_actor
from backend.db.supabase_client import get_supabase
from backend.models.audit_log import AuditAction
from backend.models.user import AccessRole, User
from backend.repositories.user_repository import UserRepository
from backend.services import audit
from backend.services.auth_service import AuthService
from backend.services.login_throttle import login_throttle

_bearer = HTTPBearer(auto_error=False)

_UNAUTHENTICATED = HTTPException(
    status.HTTP_401_UNAUTHORIZED,
    "Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_auth_service() -> AuthService:
    return AuthService(UserRepository(get_supabase()), login_throttle)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    if credentials is None or not credentials.credentials:
        raise _UNAUTHENTICATED

    try:
        payload = decode_access_token(credentials.credentials)
    except TokenError:
        raise _UNAUTHENTICATED from None

    user_id = payload.get("sub")
    if not user_id:
        raise _UNAUTHENTICATED

    user = await service.get_user(user_id)
    if user is None or not user.active:
        raise _UNAUTHENTICATED

    # Publish the actor for the audit layer, which cannot reach the request.
    set_actor(Actor(id=user.id, email=user.email, role=user.access_role.value))
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_permission(group: str) -> Callable:
    """Router-level guard for a resource group."""
    # Fail at import time, not at request time, if a router names a group that
    # does not exist.
    roles_for(group, "read")
    roles_for(group, "write")

    async def _check(request: Request, user: CurrentUser) -> User:
        if not can(user.access_role, group, request.method):
            await audit.record_event(
                action=AuditAction.ACCESS_DENIED,
                table_name=group,
                detail=f"{user.access_role.value} attempted {request.method} {request.url.path}",
            )
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"Your role ({user.access_role.value}) cannot "
                f"{action_for_method(request.method)} {group.replace('_', ' ')}",
            )
        return user

    return _check


def require_roles(*roles: AccessRole) -> Callable:
    allowed = frozenset(roles)

    async def _check(request: Request, user: CurrentUser) -> User:
        if user.access_role not in allowed:
            await audit.record_event(
                action=AuditAction.ACCESS_DENIED,
                detail=f"{user.access_role.value} attempted {request.method} {request.url.path}",
            )
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user

    return _check
