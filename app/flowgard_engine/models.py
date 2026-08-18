"""The Flowgard engine: pressure residual -> Health Deviation Index (HDI).

No routes.py by design — this module is an internal computation stage
consumed by app.prediction / app.rul / app.alert, not exposed as its own
CRUD API. Results land here so they can be inspected/audited per run.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base, TenantScopedMixin, UUIDPrimaryKeyMixin


class HealthDeviationRecord(Base, UUIDPrimaryKeyMixin, TenantScopedMixin):
    __tablename__ = "health_deviation_record"

    pump_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pump.id", ondelete="CASCADE"), nullable=False, index=True
    )
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    pressure_residual: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    health_deviation_index: Mapped[float | None] = mapped_column(Numeric(6, 3), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<HealthDeviationRecord pump_id={self.pump_id} computed_at={self.computed_at}>"
