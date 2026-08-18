"""Declarative base + shared mixins for every SQLAlchemy model in the app.

Every module's models.py imports `Base` from here to register on the same
metadata (this is what Alembic autogenerate diffs against), and every
tenant-scoped table inherits `TenantScopedMixin` — no exceptions. See the
"Multi-tenancy" section of the top-level README for the rule this enforces.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """Shared metadata for all ORM models. Import this, never create a
    second `DeclarativeBase` in a module.
    """


class UUIDPrimaryKeyMixin:
    """Gives a model a UUID primary key generated client-side."""

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    """created_at / updated_at columns, server-side so they're correct
    regardless of which process writes the row.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class TenantScopedMixin:
    """Mixin every tenant-scoped table MUST inherit.

    Auto-adds an indexed `tenant_id` FK to `tenant.id`. This is the mechanism
    that makes the "no route can query across tenants" rule enforceable:
    services filter every query by `tenant_id`, and the column existing (with
    an index) on every scoped table is what makes that filter cheap and
    consistent. The `tenant` table itself does not use this mixin — it *is*
    the tenant.
    """

    @declared_attr
    def tenant_id(cls) -> Mapped[uuid.UUID]:
        return mapped_column(
            Uuid(as_uuid=True),
            ForeignKey("tenant.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
