"""Classification model output: failure-mode class + 7-day risk score."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base, TenantScopedMixin, UUIDPrimaryKeyMixin


class PredictionResult(Base, UUIDPrimaryKeyMixin, TenantScopedMixin):
    __tablename__ = "prediction_result"

    pump_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pump.id", ondelete="CASCADE"), nullable=False, index=True
    )
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    predicted_class: Mapped[str | None] = mapped_column(String(50), nullable=True)
    risk_score_7d: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<PredictionResult pump_id={self.pump_id} computed_at={self.computed_at}>"
