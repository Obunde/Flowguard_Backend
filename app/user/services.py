"""Business logic for users.

`authenticate_user` is the one deliberate exception to tenant-scoped
queries in this module: at login time we don't know the tenant yet (the
client only has an email + password), so it looks the user up by email
alone — email is globally unique for exactly this reason (see
app/user/models.py). Once authenticated, the returned user's tenant_id is
what gets embedded in the JWT, and every other function here is
tenant-scoped as usual.
"""
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import hash_password, verify_password
from app.user.models import User
from app.user.schemas import UserCreate, UserUpdate


def create_user(db: Session, tenant_id: uuid.UUID, payload: UserCreate) -> User:
    user = User(
        tenant_id=tenant_id,
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, tenant_id: uuid.UUID, user_id: uuid.UUID) -> User | None:
    return db.scalar(select(User).where(User.id == user_id, User.tenant_id == tenant_id))


def list_users(db: Session, tenant_id: uuid.UUID) -> list[User]:
    return list(db.scalars(select(User).where(User.tenant_id == tenant_id).order_by(User.email)))


def update_user(
    db: Session, tenant_id: uuid.UUID, user_id: uuid.UUID, payload: UserUpdate
) -> User | None:
    user = get_user(db, tenant_id, user_id)
    if user is None:
        return None
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Global-by-email lookup used only by the login route. See module
    docstring for why this doesn't take tenant_id.
    """
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    user.last_login_at = datetime.now(UTC)
    db.commit()
    db.refresh(user)
    return user
