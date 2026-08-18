"""Silver-layer conforming: bronze -> sensor_reading / weather_reading /
regional_risk_score.

The actual cleaning/validation/conforming logic (deduplication, unit
normalization, outlier handling, matching bronze source_ref_id to a real
pump/station) is intentionally NOT implemented yet — these are the
transform stubs referenced in the project README. The read-side list
functions below are plain queries (used by app/feature_engineering and
tests) and are implemented.
"""
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.etl.silver.models import RegionalRiskScore, SensorReading, WeatherReading


def conform_sensor_readings(
    db: Session, tenant_id: uuid.UUID, limit: int = 500
) -> list[SensorReading]:
    """Read unprocessed `bronze_event` rows (stream=SENSOR), clean/validate,
    and upsert into `sensor_reading`. Not implemented yet.
    """
    raise NotImplementedError("silver sensor conforming is not implemented yet")


def conform_weather_readings(
    db: Session, tenant_id: uuid.UUID, limit: int = 500
) -> list[WeatherReading]:
    """Read unprocessed `bronze_event` rows (stream=WEATHER), clean/validate,
    and upsert into `weather_reading`. Not implemented yet.
    """
    raise NotImplementedError("silver weather conforming is not implemented yet")


def conform_regional_risk_scores(
    db: Session, tenant_id: uuid.UUID, limit: int = 500
) -> list[RegionalRiskScore]:
    """Read unprocessed `bronze_event` rows (stream=REGIONAL_RISK),
    clean/validate, and upsert into `regional_risk_score`. Not implemented yet.
    """
    raise NotImplementedError("silver regional risk conforming is not implemented yet")


def list_sensor_readings(
    db: Session,
    tenant_id: uuid.UUID,
    pump_id: uuid.UUID | None = None,
    since: datetime | None = None,
) -> list[SensorReading]:
    stmt = select(SensorReading).where(SensorReading.tenant_id == tenant_id)
    if pump_id is not None:
        stmt = stmt.where(SensorReading.pump_id == pump_id)
    if since is not None:
        stmt = stmt.where(SensorReading.recorded_at >= since)
    return list(db.scalars(stmt.order_by(SensorReading.recorded_at.desc())))


def list_weather_readings(
    db: Session,
    tenant_id: uuid.UUID,
    station_id: uuid.UUID | None = None,
    since: datetime | None = None,
) -> list[WeatherReading]:
    stmt = select(WeatherReading).where(WeatherReading.tenant_id == tenant_id)
    if station_id is not None:
        stmt = stmt.where(WeatherReading.station_id == station_id)
    if since is not None:
        stmt = stmt.where(WeatherReading.recorded_at >= since)
    return list(db.scalars(stmt.order_by(WeatherReading.recorded_at.desc())))


def list_regional_risk_scores(
    db: Session, tenant_id: uuid.UUID, station_id: uuid.UUID | None = None
) -> list[RegionalRiskScore]:
    stmt = select(RegionalRiskScore).where(RegionalRiskScore.tenant_id == tenant_id)
    if station_id is not None:
        stmt = stmt.where(RegionalRiskScore.station_id == station_id)
    return list(db.scalars(stmt.order_by(RegionalRiskScore.computed_at.desc())))
