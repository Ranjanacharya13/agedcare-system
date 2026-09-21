from datetime import datetime, timezone

from fastapi import HTTPException, status

from backend.config.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from backend.config.settings import get_settings
from backend.models.audit_log import AuditAction
from backend.models.user import AccessRole, User
from backend.repositories.user_repository import UserRepository
from backend.schemas.user import LoginRequest, UserCreate, UserUpdate
from backend.services import audit
from backend.services.login_throttle import LoginThrottle

_DUMMY_HASH = "$2b$12$WcQ8Xy0kZ0iZ7bF8gGm0EOoY6Hqg4Vl2N1sJqQ3rY6uT8vW0xZ1aC"

_INVALID_CREDENTIALS = "Incorrect email or password"


class AuthService:
    def __init__(self, repository: UserRepository, throttle: LoginThrottle):
        self._repository = repository
        self._throttle = throttle


    async def login(self, data: LoginRequest) -> tuple[User, str, int]:
        email = data.email.strip().lower()

        retry_after = self._throttle.blocked_for(email)
        if retry_after is not None:
            await audit.record_event(
                action=AuditAction.LOGIN_FAILED,
                detail=f"Locked out; {retry_after}s remaining",
                actor_email=email,
            )
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                "Too many failed sign-in attempts. Try again shortly.",
                headers={"Retry-After": str(retry_after)},
            )

        user = await self._repository.get_by_email(email)

        # Always run a verify, even with no user, to keep the timing flat.
        password_ok = verify_password(data.password, user.password_hash if user else _DUMMY_HASH)

        if user is None or not password_ok:
            self._throttle.record_failure(email)
            await audit.record_event(
                action=AuditAction.LOGIN_FAILED,
                detail="Unknown address or wrong password",
                actor_email=email,
            )
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, _INVALID_CREDENTIALS)

        if not user.active:
            self._throttle.record_failure(email)
            await audit.record_event(
                action=AuditAction.LOGIN_FAILED,
                record_id=str(user.id),
                detail="Account deactivated",
                actor_email=email,
            )
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, _INVALID_CREDENTIALS)

        self._throttle.clear(email)
        settings = get_settings()
        token = create_access_token(
            subject=str(user.id), role=user.access_role.value, email=user.email
        )

        await self._repository.update(
            str(user.id), {"last_login_at": datetime.now(timezone.utc).isoformat()}
        )
        await audit.record_event(
            action=AuditAction.LOGIN, record_id=str(user.id), actor_email=user.email
        )

        return user, token, settings.access_token_expire_minutes * 60

    async def get_user(self, user_id: str) -> User | None:
        return await self._repository.get_by_id(user_id)


    async def create_user(self, data: UserCreate) -> User:
        email = data.email.strip().lower()
        if await self._repository.get_by_email(email):
            raise HTTPException(status.HTTP_409_CONFLICT, "An account with that email exists")

        user = User(
            email=email,
            password_hash=hash_password(data.password),
            access_role=data.access_role,
            employee_id=data.employee_id,
            full_name=data.full_name,
            active=data.active,
        )
        created = await self._repository.create(user)
        await audit.record_data_change(
            action=AuditAction.CREATE,
            table_name="users",
            record_id=str(created.id),
            after={
                "email": created.email,
                "access_role": created.access_role.value,
                "active": created.active,
            },
        )
        return created

    async def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return await self._repository.list_all(skip, limit)

    async def update_user(self, user_id: str, data: UserUpdate, *, acting_user: User) -> User:
        existing = await self._repository.get_by_id(user_id)
        if existing is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

        updates = data.model_dump(mode="json", exclude_unset=True)
        if "email" in updates and updates["email"]:
            updates["email"] = updates["email"].strip().lower()

        # Guard against an admin locking themselves out of their own console.
        if str(existing.id) == str(acting_user.id):
            if updates.get("active") is False:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "You cannot deactivate yourself")
            if "access_role" in updates and updates["access_role"] != existing.access_role.value:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "You cannot change your own role")

        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        updated = await self._repository.update(user_id, updates)
        if updated is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

        await audit.record_data_change(
            action=AuditAction.UPDATE,
            table_name="users",
            record_id=user_id,
            before=existing.model_dump(mode="json", exclude={"password_hash"}),
            after=updated.model_dump(mode="json", exclude={"password_hash"}),
        )
        return updated

    async def change_own_password(self, user: User, current: str, new: str) -> None:
        if not verify_password(current, user.password_hash):
            await audit.record_event(
                action=AuditAction.PASSWORD_CHANGE,
                record_id=str(user.id),
                detail="Rejected: current password incorrect",
            )
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Current password is incorrect")
        if verify_password(new, user.password_hash):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "New password must differ from the current one"
            )
        await self._set_password(str(user.id), new, detail="Changed by account holder")

    async def reset_password(self, user_id: str, new: str) -> None:
        if await self._repository.get_by_id(user_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        await self._set_password(user_id, new, detail="Reset by administrator")

    async def _set_password(self, user_id: str, new_password: str, *, detail: str) -> None:
        await self._repository.update(
            user_id,
            {
                "password_hash": hash_password(new_password),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        # The new hash is never recorded — only the fact that it changed.
        await audit.record_event(
            action=AuditAction.PASSWORD_CHANGE,
            table_name="users",
            record_id=user_id,
            detail=detail,
        )

    async def delete_user(self, user_id: str, *, acting_user: User) -> None:
        if str(user_id) == str(acting_user.id):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "You cannot delete your own account")
        existing = await self._repository.get_by_id(user_id)
        if existing is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        if existing.access_role == AccessRole.ADMIN:
            remaining = [
                u
                for u in await self._repository.list_all(0, 1000)
                if u.access_role == AccessRole.ADMIN and u.active and str(u.id) != str(user_id)
            ]
            if not remaining:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, "Cannot remove the last active administrator"
                )
        await self._repository.delete(user_id)
        await audit.record_data_change(
            action=AuditAction.DELETE,
            table_name="users",
            record_id=user_id,
            before={"email": existing.email, "access_role": existing.access_role.value},
        )
