"""Bronze layer: raw landing, append-only, minimal validation.

One generic table for all three source streams (sensor telemetry, weather
API responses, regional risk source data) — the `stream` column
discriminates. Silver-layer jobs read this and write the conformed tables.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base, TenantScopedMixin, UUIDPrimaryKeyMixin


class BronzeStream(enum.StrEnum):
    SENSOR = "sensor"
    WEATHER = "weather"
    REGIONAL_RISK = "regional_risk"


class BronzeEvent(Base, UUIDPrimaryKeyMixin, TenantScopedMixin):
    __tablename__ = "bronze_event"

    stream: Mapped[BronzeStream] = mapped_column(
        Enum(BronzeStream, name="bronze_stream"), nullable=False, index=True
    )
    # Loosely-typed source identifier: pump_id for sensor events, station_id
    # for weather/regional events. Not an FK — bronze accepts data even if
    # conforming would fail, by design.
    source_ref_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)

    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<BronzeEvent id={self.id} stream={self.stream}>"
