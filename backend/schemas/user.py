from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from backend.models.user import AccessRole

MIN_PASSWORD_LENGTH = 12


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserOut"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=MIN_PASSWORD_LENGTH)
    access_role: AccessRole
    employee_id: UUID | None = None
    full_name: str | None = None
    active: bool = True


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    access_role: AccessRole | None = None
    employee_id: UUID | None = None
    full_name: str | None = None
    active: bool | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=MIN_PASSWORD_LENGTH)


class PasswordReset(BaseModel):
    """Admin-initiated reset."""

    new_password: str = Field(min_length=MIN_PASSWORD_LENGTH)


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    access_role: AccessRole
    employee_id: UUID | None = None
    full_name: str | None = None
    active: bool
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


TokenResponse.model_rebuild()
