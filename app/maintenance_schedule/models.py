"""RUL-ranked, prioritised maintenance calendar entries."""
import enum
import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base, TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class ScheduleStatus(enum.StrEnum):
    PLANNED = "planned"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ScheduledMaintenance(Base, UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "scheduled_maintenance"

    pump_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pump.id", ondelete="CASCADE"), nullable=False, index=True
    )
    station_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("station.id", ondelete="CASCADE"), nullable=False, index=True
    )
    work_order_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("work_order.id", ondelete="SET NULL"), nullable=True
    )

    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    priority_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[ScheduleStatus] = mapped_column(
        Enum(ScheduleStatus, name="schedule_status"), nullable=False, default=ScheduleStatus.PLANNED
    )
    created_from: Mapped[str | None] = mapped_column(String(50), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ScheduledMaintenance pump_id={self.pump_id} date={self.scheduled_date}>"
