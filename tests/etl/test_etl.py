"""Smoke tests for app.etl — no routes.py by design (see app/etl/README.md).

Bronze landing is exercised end-to-end including tenant scoping;
silver/gold/simulator transform logic is confirmed to run without crashing.
"""
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.etl.bronze import services as bronze_services
from app.etl.bronze.models import BronzePumpTelemetry
from app.etl.gold import services as gold_services
from app.etl.silver import services as silver_services
from app.etl.simulator import services as simulator_services


def test_bronze_landing_is_tenant_scoped(db_session: Session, tenant_a, tenant_b):
    pump_id = str(uuid.uuid4())
    reading_data = {
        "timestamp": datetime.now(UTC),
        "pump_id": pump_id,
        "vibration_axial_mm_s": 3.2,
        "vibration_radial_mm_s": 2.1,
        "temperature_bearing_c": 45.0,
        "temperature_casing_c": 50.0,
        "pressure_suction_psi": 40.0,
        "pressure_discharge_psi": 600.0,
        "motor_current_amps": 120.0,
        "motor_voltage_v": 415.0,
        "rul_hours": 1200,
        "failure_risk_7_day": 0,
    }
    
    event_a = bronze_services.ingest_telemetry_reading(
        db_session,
        tenant_a.id,
        reading_data
    )
    db_session.commit()

    events_for_a = db_session.scalars(
        select(BronzePumpTelemetry).where(BronzePumpTelemetry.tenant_id == tenant_a.id)
    ).all()
    assert [e.id for e in events_for_a] == [event_a.id]

    events_for_b = db_session.scalars(
        select(BronzePumpTelemetry).where(BronzePumpTelemetry.tenant_id == tenant_b.id)
    ).all()
    assert events_for_b == []


def test_silver_conforming_smoke(db_session: Session, tenant_a):
    # Now that Silver is implemented, just ensure the pipeline runs without crashing
    silver_services.process_bronze_to_silver(db_session, tenant_a.id)


def test_gold_aggregation_smoke(db_session: Session, tenant_a):
    # Now that Gold is implemented, ensure the pipeline runs without crashing
    gold_services.compute_and_store_gold_features(
        db_session, tenant_a.id, uuid.uuid4()
    )


def test_simulator_smoke(db_session: Session, tenant_a):
    # Now that Simulator is implemented, ensure it runs without crashing
    simulator_services.record_simulated_reading(
        db_session, tenant_a.id, str(uuid.uuid4()), wear_multiplier=0.1
    )