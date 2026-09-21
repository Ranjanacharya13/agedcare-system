from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.auth_deps import CurrentUser, get_auth_service, require_permission
from backend.models.user import AccessRole
from backend.schemas.user import (
    LoginRequest,
    PasswordChange,
    PasswordReset,
    TokenResponse,
    UserCreate,
    UserOut,
    UserUpdate,
)
from backend.services.auth_service import AuthService

router = APIRouter()

AuthDep = Annotated[AuthService, Depends(get_auth_service)]


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, service: AuthDep):
    user, token, expires_in = await service.login(data)
    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        user=UserOut(**user.model_dump(exclude={"password_hash"})),
    )


@router.get("/me", response_model=UserOut)
async def read_current_user(user: CurrentUser):
    return UserOut(**user.model_dump(exclude={"password_hash"}))


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(data: PasswordChange, user: CurrentUser, service: AuthDep):
    """Self-service, available to every signed-in role."""
    await service.change_own_password(user, data.current_password, data.new_password)


users_router = APIRouter(dependencies=[Depends(require_permission("users"))])


@users_router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate, service: AuthDep):
    user = await service.create_user(data)
    return UserOut(**user.model_dump(exclude={"password_hash"}))


@users_router.get("", response_model=list[UserOut])
async def list_users(service: AuthDep, skip: int = 0, limit: int = 100):
    return [
        UserOut(**u.model_dump(exclude={"password_hash"}))
        for u in await service.list_users(skip, limit)
    ]


@users_router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: str, service: AuthDep):
    user = await service.get_user(user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return UserOut(**user.model_dump(exclude={"password_hash"}))


@users_router.patch("/{user_id}", response_model=UserOut)
async def update_user(user_id: str, data: UserUpdate, user: CurrentUser, service: AuthDep):
    updated = await service.update_user(user_id, data, acting_user=user)
    return UserOut(**updated.model_dump(exclude={"password_hash"}))


@users_router.post("/{user_id}/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(user_id: str, data: PasswordReset, service: AuthDep):
    await service.reset_password(user_id, data.new_password)


@users_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, user: CurrentUser, service: AuthDep):
    await service.delete_user(user_id, acting_user=user)


__all__ = ["router", "users_router", "AccessRole"]
