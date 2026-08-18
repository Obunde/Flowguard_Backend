"""Gold layer: aggregated rolling-window features, computed from silver.

app/feature_engineering reads these tables (and only these — it never
reads bronze/silver directly) to build model-ready feature vectors.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base, TenantScopedMixin, UUIDPrimaryKeyMixin


class PumpFeatureWindow(Base, UUIDPrimaryKeyMixin, TenantScopedMixin):
    """Rolling-window mean/std/min/max over `sensor_reading` for one pump."""

    __tablename__ = "pump_feature_window"

    pump_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pump.id", ondelete="CASCADE"), nullable=False, index=True
    )
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    vibration_mean: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    vibration_std: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    temperature_mean: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    temperature_std: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    pressure_mean: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    pressure_std: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    motor_current_mean: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)

    sample_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<PumpFeatureWindow pump_id={self.pump_id} window_start={self.window_start}>"


class WeatherDailyRollup(Base, UUIDPrimaryKeyMixin, TenantScopedMixin):
    """Daily weather aggregate per station, rolled up from `weather_reading`."""

    __tablename__ = "weather_daily_rollup"

    station_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("station.id", ondelete="CASCADE"), nullable=False, index=True
    )
    day: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    temperature_mean: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    precipitation_total_mm: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    wind_speed_max_m_s: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<WeatherDailyRollup station_id={self.station_id} day={self.day}>"


class StationRiskComposite(Base, UUIDPrimaryKeyMixin, TenantScopedMixin):
    """Composite station risk score, rolled up from `regional_risk_score`
    (and, once implemented, weather/sensor signals).
    """

    __tablename__ = "station_risk_composite"

    station_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("station.id", ondelete="CASCADE"), nullable=False, index=True
    )
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    composite_score: Mapped[float | None] = mapped_column(Numeric(6, 3), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<StationRiskComposite station_id={self.station_id} computed_at={self.computed_at}>"
