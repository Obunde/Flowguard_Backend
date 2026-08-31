"""Smoke tests for app.flowgard_engine — no routes.py by design (see module
docstring), so this only exercises the service layer directly.
"""
import uuid

import pytest
from sqlalchemy.orm import Session

from app.flowgard_engine import services


def test_list_is_tenant_scoped_and_empty_for_unknown_pump(db_session: Session, tenant_a):
    assert services.list_health_deviations(db_session, tenant_a.id) == []
    assert services.get_latest_health_deviation(db_session, tenant_a.id, uuid.uuid4()) is None


def test_compute_health_deviation_success(db_session: Session, station_a):
    from app.pump.models import Pump, PumpStatus

    pump = Pump(
        tenant_id=station_a.tenant_id,
        station_id=station_a.id,
        tag_number="PS1-P01",
        status=PumpStatus.OPERATIONAL,
        rated_pressure_kpa=4500.0,
    )
    db_session.add(pump)
    db_session.commit()
    db_session.refresh(pump)

    record = services.compute_health_deviation(db_session, station_a.tenant_id, pump.id)
    assert record is not None
    assert record.pump_id == pump.id
    assert record.tenant_id == station_a.tenant_id
    assert record.health_deviation_index is not None
    assert 0.0 <= record.health_deviation_index <= 1.0

    latest = services.get_latest_health_deviation(db_session, station_a.tenant_id, pump.id)
    assert latest.id == record.id


def test_compute_health_deviation_invalid_pump(db_session: Session, tenant_a):
    with pytest.raises(ValueError):
        services.compute_health_deviation(db_session, tenant_a.id, uuid.uuid4())

