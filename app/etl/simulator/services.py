"""Continuous synthetic sensor-feed generator — a stand-in for a real SCADA
feed during development. Writes into app.etl.bronze like any other source.

Generation logic (what a realistic vibration/temperature/pressure/motor
current signal looks like, including injected drift/fault scenarios) is not
implemented yet.
"""
import uuid

from sqlalchemy.orm import Session


def generate_sensor_reading(pump_id: uuid.UUID) -> dict:
    """Produce one synthetic reading payload for a pump. Not implemented yet."""
    raise NotImplementedError("synthetic sensor reading generation is not implemented yet")


def run_simulator_once(db: Session, tenant_id: uuid.UUID) -> int:
    """Generate one reading per active pump for a tenant and land it via
    app.etl.bronze.services.land_event. Returns the number of events landed.
    Not implemented yet.
    """
    raise NotImplementedError("simulator tick is not implemented yet")


async def run_simulator_forever(tenant_id: uuid.UUID) -> None:
    """Loop `run_simulator_once` every `settings.simulator_interval_seconds`.
    Intended to run as a background task/process, not inline in a request.
    Not implemented yet.
    """
    raise NotImplementedError("simulator loop is not implemented yet")
