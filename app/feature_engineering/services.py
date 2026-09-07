"""Reads Gold-layer tables (app.etl.gold), produces model-ready feature
vectors for prediction / rul / flowgard_engine / explainability.

No models.py/routes.py/schemas.py here by design — this module has no
tables of its own and no HTTP surface; it's a pure read+transform layer
sitting between ETL and the modelling modules. Feature computation logic is
not implemented yet.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.etl.gold.models import GoldPumpFeatures
from app.flowgard_engine.models import HealthDeviationRecord
from app.pump.models import Pump


def build_feature_vector(db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID) -> dict[str, float]:
    """Assemble the latest model-ready feature vector for one pump from
    Gold-layer rolling-window features and engine metrics.
    """
    pump = db.scalar(select(Pump).where(Pump.id == pump_id, Pump.tenant_id == tenant_id))
    if pump is None:
        raise ValueError(f"Pump {pump_id} not found for tenant {tenant_id}")

    gold = db.scalar(
        select(GoldPumpFeatures)
        .where(GoldPumpFeatures.tenant_id == tenant_id, GoldPumpFeatures.pump_id == pump_id)
        .order_by(GoldPumpFeatures.timestamp.desc())
        .limit(1)
    )

    hdi = db.scalar(
        select(HealthDeviationRecord)
        .where(HealthDeviationRecord.tenant_id == tenant_id, HealthDeviationRecord.pump_id == pump_id)
        .order_by(HealthDeviationRecord.computed_at.desc())
        .limit(1)
    )

    hdi_val = float(hdi.health_deviation_index) if hdi and hdi.health_deviation_index is not None else 0.1
    prior_count = float(pump.prior_intervention_count or 0)

    if gold:
        vib_avg = float(gold.vibration_axial_rolling_avg or 1.5)
        vib_std = float(gold.vibration_axial_rolling_std or 0.1)
        temp_avg = float(gold.temperature_bearing_rolling_avg or 45.0)
        temp_max = float(gold.temperature_bearing_rolling_max or 50.0)
        press_avg = float(gold.pressure_discharge_rolling_avg or 600.0)
        motor_curr = float(gold.motor_current_amps or 120.0)
    else:
        vib_avg = 1.5
        vib_std = 0.1
        temp_avg = 45.0
        temp_max = 50.0
        press_avg = 600.0
        motor_curr = 120.0

    return {
        "vibration_axial_rolling_avg": vib_avg,
        "vibration_axial_rolling_std": vib_std,
        "temperature_bearing_rolling_avg": temp_avg,
        "temperature_bearing_rolling_max": temp_max,
        "pressure_discharge_rolling_avg": press_avg,
        "motor_current_amps": motor_curr,
        "health_deviation_index": hdi_val,
        "prior_intervention_count": prior_count,
    }


def build_feature_batch(
    db: Session, tenant_id: uuid.UUID, pump_ids: list[uuid.UUID]
) -> dict[uuid.UUID, dict[str, float]]:
    """Batch version of `build_feature_vector`, used by scheduled scoring
    runs across a tenant's fleet.
    """
    return {pid: build_feature_vector(db, tenant_id, pid) for pid in pump_ids}
