"""Maintenance work orders: interventions raised from alerts, the schedule,
or manually.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base, TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class WorkOrderStatus(enum.StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkOrderSource(enum.StrEnum):
    MANUAL = "manual"
    ALERT = "alert"
    SCHEDULE = "schedule"


class WorkOrder(Base, UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "work_order"

    pump_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pump.id", ondelete="CASCADE"), nullable=False, index=True
    )
    station_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("station.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    assigned_to_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[WorkOrderStatus] = mapped_column(
        Enum(WorkOrderStatus, name="work_order_status"),
        nullable=False,
        default=WorkOrderStatus.OPEN,
    )
    source: Mapped[WorkOrderSource] = mapped_column(
        Enum(WorkOrderSource, name="work_order_source"),
        nullable=False,
        default=WorkOrderSource.MANUAL,
    )
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="normal")

    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<WorkOrder id={self.id} status={self.status}>"
