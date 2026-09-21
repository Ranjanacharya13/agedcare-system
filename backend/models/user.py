from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class AccessRole(StrEnum):
    """Authorisation role — deliberately separate from `EmployeeRole`."""

    ADMIN = "Admin"
    MANAGER = "Manager"
    NURSE = "Nurse"
    CARE_WORKER = "Care Worker"
    FAMILY = "Family"


STAFF_ROLES = frozenset(
    {AccessRole.ADMIN, AccessRole.MANAGER, AccessRole.NURSE, AccessRole.CARE_WORKER}
)

#: Roles allowed to change organisation-wide configuration and other accounts.
PRIVILEGED_ROLES = frozenset({AccessRole.ADMIN, AccessRole.MANAGER})


class User(BaseModel):
    """A login account."""

    id: UUID | None = None
    email: EmailStr
    password_hash: str
    access_role: AccessRole
    employee_id: UUID | None = None
    full_name: str | None = None
    active: bool = True
    last_login_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
