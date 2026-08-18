"""Remaining Useful Life regression output, with MC Dropout confidence
intervals.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base, TenantScopedMixin, UUIDPrimaryKeyMixin


class RulEstimate(Base, UUIDPrimaryKeyMixin, TenantScopedMixin):
    __tablename__ = "rul_estimate"

    pump_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pump.id", ondelete="CASCADE"), nullable=False, index=True
    )
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    remaining_useful_life_days: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    confidence_lower_days: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    confidence_upper_days: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    mc_dropout_samples: Mapped[int | None] = mapped_column(Integer, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<RulEstimate pump_id={self.pump_id} computed_at={self.computed_at}>"
