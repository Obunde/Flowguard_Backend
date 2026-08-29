"""Business logic for the Flowgard engine: pressure residual -> Health
Deviation Index. The core math is not implemented yet (this is what "we'll
fill in Flowgard math module by module" refers to); read access to prior
results is implemented since app.prediction/app.alert will need it.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from datetime import datetime, timezone

from app.etl.gold.models import PumpFeatureWindow
from app.flowgard_engine.models import HealthDeviationRecord
from app.pump.models import Pump


def compute_health_deviation(
    db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID
) -> HealthDeviationRecord:
    """Compute pressure residual from the latest feature vector (app.etl.gold)
    or pump baseline parameters, and derive the Health Deviation Index (HDI).
    """
    pump = db.scalar(select(Pump).where(Pump.id == pump_id, Pump.tenant_id == tenant_id))
    if pump is None:
        raise ValueError(f"Pump {pump_id} not found for tenant {tenant_id}")

    rated_pressure = float(pump.rated_pressure_kpa) if pump.rated_pressure_kpa is not None else 4000.0

    # Retrieve latest feature window from ETL Gold layer
    gold_window = db.scalar(
        select(PumpFeatureWindow)
        .where(PumpFeatureWindow.tenant_id == tenant_id, PumpFeatureWindow.pump_id == pump_id)
        .order_by(PumpFeatureWindow.window_end.desc())
        .limit(1)
    )

    if gold_window and gold_window.pressure_mean is not None:
        actual_pressure = float(gold_window.pressure_mean)
        vibration_val = float(gold_window.vibration_mean) if gold_window.vibration_mean is not None else 1.5
    else:
        # Baseline/default telemetry values if gold features haven't run yet
        actual_pressure = rated_pressure * 0.95
        vibration_val = 1.5

    pressure_residual = abs(actual_pressure - rated_pressure)
    norm_residual = min(1.0, pressure_residual / max(1.0, rated_pressure))
    norm_vibration = min(1.0, vibration_val / 10.0)

    # Health Deviation Index on scale [0.0, 1.0]
    hdi = round(min(1.0, max(0.0, 0.6 * norm_residual + 0.4 * norm_vibration)), 3)

    record = HealthDeviationRecord(
        tenant_id=tenant_id,
        pump_id=pump_id,
        computed_at=datetime.now(timezone.utc),
        pressure_residual=round(pressure_residual, 4),
        health_deviation_index=hdi,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_latest_health_deviation(
    db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID
) -> HealthDeviationRecord | None:
    stmt = (
        select(HealthDeviationRecord)
        .where(
            HealthDeviationRecord.tenant_id == tenant_id,
            HealthDeviationRecord.pump_id == pump_id,
        )
        .order_by(HealthDeviationRecord.computed_at.desc())
        .limit(1)
    )
    return db.scalar(stmt)


def list_health_deviations(
    db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID | None = None
) -> list[HealthDeviationRecord]:
    stmt = select(HealthDeviationRecord).where(HealthDeviationRecord.tenant_id == tenant_id)
    if pump_id is not None:
        stmt = stmt.where(HealthDeviationRecord.pump_id == pump_id)
    return list(db.scalars(stmt.order_by(HealthDeviationRecord.computed_at.desc())))
