"""Auth dependency: JWT decode -> user -> tenant + role.

This is the only place that issues/decodes tokens or hashes passwords.
`get_current_user` is the dependency every protected route (indirectly, via
app/core/tenancy.py) depends on. It revalidates active status and role against the database —
the token identifies the session while the database remains authoritative for
account status and effective authorization.
"""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.permissions import Permission, has_permission
from app.user.models import User

# tokenUrl points at the user module's login route — see app/user/routes.py.
# This is metadata for OpenAPI docs only; auth.py does not import app.user.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login", auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    """The decoded identity attached to a request. `tenant_id` is what
    app/core/tenancy.py hands to every service call.
    """

    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    role: str


def hash_password(plain_password: str) -> str:
    # bcrypt truncates at 72 bytes silently — reject longer input explicitly
    # rather than hashing a truncated password the user didn't type.
    encoded = plain_password.encode("utf-8")
    if len(encoded) > 72:
        raise ValueError("password must be at most 72 bytes")
    return bcrypt.hashpw(encoded, bcrypt.gensalt()).decode("ascii")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("ascii"))
    except ValueError:
        return False


def create_access_token(
    *,
    user_id: uuid.UUID,
    tenant_id: uuid.UUID,
    email: str,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    payload = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "email": email,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> CurrentUser:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    try:
        return CurrentUser(
            id=uuid.UUID(payload["sub"]),
            tenant_id=uuid.UUID(payload["tenant_id"]),
            email=payload["email"],
            role=payload["role"],
        )
    except (KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token payload",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def get_current_user(
    token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> CurrentUser:
    """The base identity dependency. No token -> 401, so any route that
    depends on this (directly or via app/core/tenancy.py) cannot be called
    without tenant context.
    """
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    decoded = decode_access_token(token)
    user = db.scalar(
        select(User).where(
            User.id == decoded.id,
            User.tenant_id == decoded.tenant_id,
            User.is_active.is_(True),
        )
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive or unavailable",
        )
    return CurrentUser(
        id=user.id,
        tenant_id=user.tenant_id,
        email=user.email,
        role=user.role.value,
    )


def require_role(*allowed_roles: str):
    """Dependency factory for role-gated routes, e.g.:
    `Depends(require_role("admin", "planner"))`.
    """

    def _check(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return current_user

    return _check


def require_permission(permission: Permission):
    """Deny-by-default permission dependency for protected operations."""

    def _check(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not has_permission(current_user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission.value}",
            )
        return current_user

    return _check
