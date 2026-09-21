"""Pydantic v2 request/response models for the user module."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.user.models import UserRole


def _reject_platform_admin(role: UserRole | None) -> UserRole | None:
    """Tenant admins manage tenant users only; platform_admin is seed-only."""
    if role == UserRole.PLATFORM_ADMIN:
        raise ValueError("platform_admin cannot be assigned through user management")
    return role


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.VIEWER


class UserCreate(UserBase):
    """Invite for a new user — no password; one is generated and emailed."""

    _check_role = field_validator("role")(_reject_platform_admin)


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None

    _check_role = field_validator("role")(_reject_platform_admin)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID | None = None
    is_active: bool
    must_reset_password: bool
    last_login_at: datetime | None = None


class ResetPasswordRequest(BaseModel):
    """First-login password change; `reset_token` comes from the login route."""

    reset_token: str
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    """`access_token` on a normal login; `reset_required` + `reset_token` on a
    first login."""

    token_type: str = "bearer"
    reset_required: bool = False
    access_token: str | None = None
    reset_token: str | None = None
