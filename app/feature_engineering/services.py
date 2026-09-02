"""Reads ETL Gold tables (`app.etl.gold`) and flattens them into model-ready
feature vectors for prediction / rul / flowgard_engine / explainability.

No `models.py` / `routes.py` here by design — this module owns no tables and
has no HTTP surface. It is a pure read + transform layer between ETL and the
modelling modules. `schemas.py` (allowed for an HTTP-less module, cf.
`app/flowgard_engine/schemas.py`) holds the one definition of the vector's
shape.

Data sources, all Gold-only (never bronze/silver):

===============  =========================  ===================================
Tier             Table                      Join key
===============  =========================  ===================================
sensor stats     ``PumpFeatureWindow``      ``pump_id``
weather context  ``WeatherDailyRollup``     pump -> ``station_id``
regional risk    ``StationRiskComposite``   pump -> ``station_id``
===============  =========================  ===================================

The pump -> station lookup goes through `app.pump.models.Pump`, matching what
`prediction` / `flowgard_engine` / `explainability` already do.

**Freshness policy.** The sensor window is a live signal (~1 min cadence): if
the newest one for a pump is older than `MAX_WINDOW_AGE` a live risk decision
should not be made on it, so `build_feature_vector` raises
`StaleFeatureDataError`. Weather and risk update on a much slower cadence by
design, so an old — or entirely absent — weather/risk join is *not* an error:
those fields fall back to ``0.0`` and a companion ``*_data_available`` flag is
set to ``0.0`` so a downstream model / SHAP can tell "genuinely zero" from
"not joined". A NULL numeric column inside an otherwise-valid window is
likewise filled with ``0.0`` (``sample_count`` is carried through so a thin
window can still be down-weighted).

`build_feature_batch` is for scheduled fleet-wide scoring: it never raises for
a single bad pump — a pump with no fresh window is simply omitted from the
returned mapping (callers that need to tell "stale" from "never existed"
should call `build_feature_vector` per pump).
"""
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.etl.gold.models import PumpFeatureWindow, StationRiskComposite, WeatherDailyRollup
from app.feature_engineering.schemas import FeatureVector
from app.pump.models import Pump

# A sensor window older than this is considered too stale to score a live
# risk decision on. Chosen against the ~1-minute raw sensor cadence: an hour
# is dozens of missed windows, i.e. a real ingestion gap rather than jitter.
MAX_WINDOW_AGE = timedelta(hours=1)


class FeatureEngineeringError(Exception):
    """Base for the two conditions a caller is expected to branch on."""


class FeatureVectorUnavailableError(FeatureEngineeringError):
    """No `PumpFeatureWindow` exists at all for this pump/tenant yet."""

    def __init__(self, tenant_id: uuid.UUID, pump_id: uuid.UUID) -> None:
        self.tenant_id = tenant_id
        self.pump_id = pump_id
        super().__init__(
            f"no feature window for pump {pump_id} (tenant {tenant_id}); "
            "ETL Gold has produced nothing for this pump"
        )


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
            f"{last_window_end.isoformat()}, older than the {MAX_WINDOW_AGE} freshness limit"
        )


# --------------------------------------------------------------------------- #
# internal helpers
# --------------------------------------------------------------------------- #
def _f(value: object) -> float:
    """Gold numeric columns come back as `Decimal | None` — normalise to a
    plain float, treating NULL as 0.0."""
    return float(value) if value is not None else 0.0


def _aware(moment: datetime) -> datetime:
    """Rows written with a naive timestamp are stored as UTC — make them
    comparable to `datetime.now(UTC)`."""
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
    """One query: the newest row of `model` per `group_col` value, restricted
    to `tenant_id` and `ids`. Portable (group-by-max + self-join, no
    DISTINCT ON). Ties on `order_col` are broken arbitrarily but
    deterministically per run."""
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


# --------------------------------------------------------------------------- #
# public API
# --------------------------------------------------------------------------- #
def build_feature_vector(
    db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID
) -> dict[str, float]:
    """Assemble the latest model-ready feature vector for one pump.

    Raises `FeatureVectorUnavailableError` if ETL Gold has produced no window
    for the pump, `StaleFeatureDataError` if the newest window is older than
    `MAX_WINDOW_AGE`, and `ValueError` if `pump_id` is not a pump in this
    tenant. A missing weather / risk join is not an error (see module docs).
    """
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
    """Batched `build_feature_vector` for scheduled fleet-wide scoring.

    Issues a fixed number of queries (one per data source) regardless of
    ``len(pump_ids)``. A pump with no window, or whose newest window is
    stale, is **omitted** from the result rather than raising — a fleet
    scoring run should not abort over one lagging pump. Callers needing to
    distinguish "stale" from "never existed" should fall back to
    `build_feature_vector` per pump.
    """
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
    fresh = {
        pid: win
        for pid, win in windows.items()
        if not _is_stale(win, now)
    }
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
        if station_id is None:
            # Window exists but no matching pump row in this tenant — skip
            # rather than emit a vector that looks real.
            continue
        result[pid] = _assemble(
            window,
            weather_by_station.get(station_id),
            risk_by_station.get(station_id),
        )
    return result
