"""Smoke tests for app.etl — no routes.py by design (see app/etl/README.md).

Bronze landing (plain persistence) is exercised end-to-end including tenant
scoping; silver/gold/simulator transform logic is confirmed to be the
documented NotImplementedError stubs.
"""
import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy.orm import Session

from app.etl.bronze import services as bronze_services
from app.etl.bronze.models import BronzeStream
from app.etl.gold import services as gold_services
from app.etl.silver import services as silver_services
from app.etl.simulator import services as simulator_services


def test_bronze_landing_is_tenant_scoped(db_session: Session, tenant_a, tenant_b):
    event_a = bronze_services.land_event(
        db_session,
        tenant_a.id,
        BronzeStream.SENSOR,
        payload={"vibration_mm_s": 3.2},
        recorded_at=datetime.now(UTC),
    )

    events_for_a = bronze_services.list_unprocessed_events(
        db_session, tenant_a.id, BronzeStream.SENSOR
    )
    assert [e.id for e in events_for_a] == [event_a.id]

    events_for_b = bronze_services.list_unprocessed_events(
        db_session, tenant_b.id, BronzeStream.SENSOR
    )
    assert events_for_b == []


def test_silver_conforming_not_implemented(db_session: Session, tenant_a):
    with pytest.raises(NotImplementedError):
        silver_services.conform_sensor_readings(db_session, tenant_a.id)


def test_gold_aggregation_not_implemented(db_session: Session, tenant_a):
    with pytest.raises(NotImplementedError):
        gold_services.compute_pump_feature_windows(
            db_session, tenant_a.id, uuid.uuid4(), window=None
        )


def test_simulator_not_implemented(tenant_a):
    with pytest.raises(NotImplementedError):
        simulator_services.generate_sensor_reading(uuid.uuid4())
