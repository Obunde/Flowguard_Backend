"""Reads ETL Gold tables and flattens them into model-ready feature vectors
for prediction / rul / flowgard_engine / explainability. Pure read+transform,
Gold-only, no tables or HTTP surface of its own.

Sources: PumpFeatureWindow (by pump_id), WeatherDailyRollup and
StationRiskComposite (by the pump's station_id, looked up via
`app.pump.models.Pump`).

Freshness: the sensor window is a live signal, so `build_feature_vector`
raises `StaleFeatureDataError` when the newest one is older than
`MAX_WINDOW_AGE`, and `FeatureVectorUnavailableError` when none exists.
Weather/risk update slowly, so a missing or old join is not an error — those
fields fall back to 0.0 with a `*_data_available` flag at 0.0. A NULL column
inside a valid window fills 0.0. `build_feature_batch` never raises for one
bad pump: pumps without a fresh window are omitted from the result.
"""
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.etl.gold.models import PumpFeatureWindow, StationRiskComposite, WeatherDailyRollup
from app.feature_engineering.schemas import FeatureVector
from app.pump.models import Pump

# ~1-minute raw sensor cadence, so an hour is dozens of missed windows.
MAX_WINDOW_AGE = timedelta(hours=1)


class FeatureEngineeringError(Exception):
    """Base for the two conditions a caller branches on."""


class FeatureVectorUnavailableError(FeatureEngineeringError):
    """No `PumpFeatureWindow` exists for this pump/tenant yet."""

    def __init__(self, tenant_id: uuid.UUID, pump_id: uuid.UUID) -> None:
        self.tenant_id = tenant_id
        self.pump_id = pump_id
        super().__init__(f"no feature window for pump {pump_id} (tenant {tenant_id})")


class StaleFeatureDataError(FeatureEngineeringError):
    """The newest `PumpFeatureWindow` is older than `MAX_WINDOW_AGE`."""

    def __init__(
        self, tenant_id: uuid.UUID, pump_id: uuid.UUID, last_window_end: datetime
    ) -> None:
        self.tenant_id = tenant_id
        self.pump_id = pump_id
        self.last_window_end = last_window_end
        super().__init__(
            f"newest feature window for pump {pump_id} (tenant {tenant_id}) ends at "
            f"{last_window_end.isoformat()}, older than the {MAX_WINDOW_AGE} limit"
        )


def _f(value: object) -> float:
    """Decimal | None from a Gold column -> float, NULL as 0.0."""
    return float(value) if value is not None else 0.0


def _aware(moment: datetime) -> datetime:
    """Naive timestamps are stored as UTC — make them comparable to now(UTC)."""
    return moment if moment.tzinfo is not None else moment.replace(tzinfo=UTC)


def _is_stale(window: PumpFeatureWindow, now: datetime) -> bool:
    return (now - _aware(window.window_end)) > MAX_WINDOW_AGE


def _assemble(
    window: PumpFeatureWindow,
    weather: WeatherDailyRollup | None,
    risk: StationRiskComposite | None,
) -> dict[str, float]:
    vector = FeatureVector(
        vibration_mean=_f(window.vibration_mean),
        vibration_std=_f(window.vibration_std),
        temperature_mean=_f(window.temperature_mean),
        temperature_std=_f(window.temperature_std),
        pressure_mean=_f(window.pressure_mean),
        pressure_std=_f(window.pressure_std),
        motor_current_mean=_f(window.motor_current_mean),
        sample_count=_f(window.sample_count),
        weather_temperature_mean=_f(weather.temperature_mean) if weather else 0.0,
        weather_precipitation_total_mm=_f(weather.precipitation_total_mm) if weather else 0.0,
        weather_wind_speed_max_m_s=_f(weather.wind_speed_max_m_s) if weather else 0.0,
        weather_data_available=1.0 if weather else 0.0,
        regional_risk_score=_f(risk.composite_score) if risk else 0.0,
        risk_data_available=1.0 if risk else 0.0,
    )
    return vector.as_dict()


def _latest_per_group(
    db: Session,
    model: type,
    group_col,
    order_col,
    tenant_id: uuid.UUID,
    ids: list[uuid.UUID],
) -> dict[uuid.UUID, object]:
    """One query: newest row of `model` per `group_col`, scoped to `tenant_id`
    and `ids`. Portable group-by-max + self-join (no DISTINCT ON)."""
    if not ids:
        return {}
    newest = (
        select(group_col.label("gid"), func.max(order_col).label("max_order"))
        .where(model.tenant_id == tenant_id, group_col.in_(ids))
        .group_by(group_col)
        .subquery()
    )
    stmt = select(model).join(
        newest,
        (group_col == newest.c.gid) & (order_col == newest.c.max_order),
    )
    out: dict[uuid.UUID, object] = {}
    for row in db.scalars(stmt):
        out.setdefault(getattr(row, group_col.key), row)
    return out


def build_feature_vector(
    db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID
) -> dict[str, float]:
    """Latest feature vector for one pump. Raises `FeatureVectorUnavailableError`
    (no window), `StaleFeatureDataError` (window too old), or `ValueError`
    (pump not in this tenant)."""
    window = db.scalar(
        select(PumpFeatureWindow)
        .where(
            PumpFeatureWindow.tenant_id == tenant_id,
            PumpFeatureWindow.pump_id == pump_id,
        )
        .order_by(PumpFeatureWindow.window_end.desc())
        .limit(1)
    )
    if window is None:
        raise FeatureVectorUnavailableError(tenant_id, pump_id)
    if _is_stale(window, datetime.now(UTC)):
        raise StaleFeatureDataError(tenant_id, pump_id, _aware(window.window_end))

    pump = db.scalar(select(Pump).where(Pump.id == pump_id, Pump.tenant_id == tenant_id))
    if pump is None:
        raise ValueError(f"Pump {pump_id} not found for tenant {tenant_id}")

    weather = db.scalar(
        select(WeatherDailyRollup)
        .where(
            WeatherDailyRollup.tenant_id == tenant_id,
            WeatherDailyRollup.station_id == pump.station_id,
        )
        .order_by(WeatherDailyRollup.day.desc())
        .limit(1)
    )
    risk = db.scalar(
        select(StationRiskComposite)
        .where(
            StationRiskComposite.tenant_id == tenant_id,
            StationRiskComposite.station_id == pump.station_id,
        )
        .order_by(StationRiskComposite.computed_at.desc())
        .limit(1)
    )
    return _assemble(window, weather, risk)


def build_feature_batch(
    db: Session, tenant_id: uuid.UUID, pump_ids: list[uuid.UUID]
) -> dict[uuid.UUID, dict[str, float]]:
    """Batched `build_feature_vector` for fleet-wide scoring. Fixed query count
    regardless of `len(pump_ids)`; pumps without a fresh window are omitted
    rather than raising."""
    unique_ids = list(dict.fromkeys(pump_ids))
    if not unique_ids:
        return {}

    now = datetime.now(UTC)

    windows = _latest_per_group(
        db,
        PumpFeatureWindow,
        PumpFeatureWindow.pump_id,
        PumpFeatureWindow.window_end,
        tenant_id,
        unique_ids,
    )
    fresh = {pid: win for pid, win in windows.items() if not _is_stale(win, now)}
    if not fresh:
        return {}

    pump_rows = db.execute(
        select(Pump.id, Pump.station_id).where(
            Pump.tenant_id == tenant_id, Pump.id.in_(list(fresh))
        )
    ).all()
    station_by_pump = {pid: sid for pid, sid in pump_rows}
    station_ids = list({sid for sid in station_by_pump.values() if sid is not None})

    weather_by_station = _latest_per_group(
        db,
        WeatherDailyRollup,
        WeatherDailyRollup.station_id,
        WeatherDailyRollup.day,
        tenant_id,
        station_ids,
    )
    risk_by_station = _latest_per_group(
        db,
        StationRiskComposite,
        StationRiskComposite.station_id,
        StationRiskComposite.computed_at,
        tenant_id,
        station_ids,
    )

    result: dict[uuid.UUID, dict[str, float]] = {}
    for pid, window in fresh.items():
        station_id = station_by_pump.get(pid)
        if station_id is None:  # window with no matching pump row in this tenant
            continue
        result[pid] = _assemble(
            window,
            weather_by_station.get(station_id),
            risk_by_station.get(station_id),
        )
    return result
