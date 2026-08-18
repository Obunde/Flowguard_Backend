"""Silver layer: cleaned, conformed data.

`sensor_reading`, `weather_reading`, `regional_risk_score` — the three
tables app/etl is the exclusive writer of. Every other module reads these
(if at all) through app/feature_engineering, never directly.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base, TenantScopedMixin, UUIDPrimaryKeyMixin


class SensorReading(Base, UUIDPrimaryKeyMixin, TenantScopedMixin):
    __tablename__ = "sensor_reading"

    pump_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pump.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    vibration_mm_s: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    temperature_c: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    pressure_kpa: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    motor_current_a: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SensorReading pump_id={self.pump_id} recorded_at={self.recorded_at}>"


class WeatherReading(Base, UUIDPrimaryKeyMixin, TenantScopedMixin):
    __tablename__ = "weather_reading"

    station_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("station.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    temperature_c: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    humidity_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    precipitation_mm: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    wind_speed_m_s: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<WeatherReading station_id={self.station_id} recorded_at={self.recorded_at}>"


class RegionalRiskScore(Base, UUIDPrimaryKeyMixin, TenantScopedMixin):
    __tablename__ = "regional_risk_score"

    station_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("station.id", ondelete="CASCADE"), nullable=False, index=True
    )
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    population_density_score: Mapped[float | None] = mapped_column(Numeric(6, 3), nullable=True)
    incident_history_score: Mapped[float | None] = mapped_column(Numeric(6, 3), nullable=True)
    land_use_score: Mapped[float | None] = mapped_column(Numeric(6, 3), nullable=True)
    composite_score: Mapped[float | None] = mapped_column(Numeric(6, 3), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<RegionalRiskScore station_id={self.station_id} computed_at={self.computed_at}>"
