"""Gold-layer aggregation: rolling-window feature computation over silver
data. The compute functions are stubs — the aggregation math (window
sizing, mean/std/trend calculation) is not implemented yet. Read-side list
functions are implemented since app/feature_engineering depends on them.
"""
import uuid
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.etl.gold.models import PumpFeatureWindow, StationRiskComposite, WeatherDailyRollup


def compute_pump_feature_windows(
    db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID, window: timedelta
) -> list[PumpFeatureWindow]:
    """Aggregate `sensor_reading` into rolling windows for one pump. Not
    implemented yet.
    """
    raise NotImplementedError("gold pump feature window computation is not implemented yet")


def compute_weather_daily_rollups(
    db: Session, tenant_id: uuid.UUID, station_id: uuid.UUID, day: datetime
) -> WeatherDailyRollup:
    """Aggregate `weather_reading` into a daily rollup for one station. Not
    implemented yet.
    """
    raise NotImplementedError("gold weather daily rollup computation is not implemented yet")


def compute_station_risk_composite(
    db: Session, tenant_id: uuid.UUID, station_id: uuid.UUID
) -> StationRiskComposite:
    """Aggregate `regional_risk_score` (and related signals) into a
    composite station risk score. Not implemented yet.
    """
    raise NotImplementedError("gold station risk composite computation is not implemented yet")


def list_pump_feature_windows(
    db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID | None = None
) -> list[PumpFeatureWindow]:
    stmt = select(PumpFeatureWindow).where(PumpFeatureWindow.tenant_id == tenant_id)
    if pump_id is not None:
        stmt = stmt.where(PumpFeatureWindow.pump_id == pump_id)
    return list(db.scalars(stmt.order_by(PumpFeatureWindow.window_start.desc())))


def list_station_risk_composites(
    db: Session, tenant_id: uuid.UUID, station_id: uuid.UUID | None = None
) -> list[StationRiskComposite]:
    stmt = select(StationRiskComposite).where(StationRiskComposite.tenant_id == tenant_id)
    if station_id is not None:
        stmt = stmt.where(StationRiskComposite.station_id == station_id)
    return list(db.scalars(stmt.order_by(StationRiskComposite.computed_at.desc())))
