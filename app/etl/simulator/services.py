from datetime import datetime
from uuid import UUID

import numpy as np
from sqlalchemy.orm import Session

from app.etl.bronze.models import BronzePumpTelemetry

# Sensor physics, shared by live generation and ML training data. Changing a
# coefficient here changes both — keep them in one place.
SENSOR_MODEL = {
    "vibration_axial_mm_s": (2.5, 0.2, 6.5),
    "vibration_radial_mm_s": (2.2, 0.2, 5.0),
    "temperature_bearing_c": (65.0, 1.5, 35.0),
    "temperature_casing_c": (55.0, 1.0, 20.0),
    "pressure_suction_psi": (45.0, 2.0, 0.0),
    "pressure_discharge_psi": (600.0, 10.0, -80.0),
    "motor_current_amps": (120.0, 2.5, 45.0),
    "motor_voltage_v": (415.0, 5.0, 0.0),
}

FAILURE_WEAR_THRESHOLD = 0.8
RUL_HOURS_AT_NEW = 1200


def sample_readings(wear: np.ndarray, rng: np.random.Generator) -> dict[str, np.ndarray]:
    """Vectorised sensor sampling: one row per wear level in `wear`."""
    out: dict[str, np.ndarray] = {}
    for name, (base, noise, slope) in SENSOR_MODEL.items():
        out[name] = np.round(rng.normal(base, noise, size=wear.shape) + wear * slope, 2)
    out["rul_hours"] = np.maximum(0, (RUL_HOURS_AT_NEW - wear * RUL_HOURS_AT_NEW).astype(int))
    out["failure_risk_7_day"] = (wear > FAILURE_WEAR_THRESHOLD).astype(int)
    return out


def generate_live_reading(
    tenant_id: UUID | str, pump_id: UUID | str, wear_multiplier: float
) -> dict:
    """Simulates a single sensor reading with progressive degradation for a specific tenant pump."""
    sampled = sample_readings(np.array([wear_multiplier], dtype=float), np.random.default_rng())
    row = {name: values[0].item() for name, values in sampled.items()}
    return {
        "tenant_id": UUID(str(tenant_id)) if not isinstance(tenant_id, UUID) else tenant_id,
        "timestamp": datetime.now(),
        "pump_id": UUID(str(pump_id)) if not isinstance(pump_id, UUID) else pump_id,
        **row,
    }


def record_simulated_reading(
    session: Session, tenant_id: UUID | str, pump_id: UUID | str, wear_multiplier: float
) -> BronzePumpTelemetry:
    """Generates and writes a single simulated telemetry record to Bronze storage."""
    payload = generate_live_reading(tenant_id, pump_id, wear_multiplier)
    reading = BronzePumpTelemetry(**payload)
    session.add(reading)
    session.commit()
    session.refresh(reading)
    return reading
