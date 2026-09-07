"""Smoke test for app.feature_engineering — services.py only, no HTTP surface."""
import uuid

import pytest
from sqlalchemy.orm import Session

from app.feature_engineering import services
from app.pump.models import Pump, PumpStatus
from app.station.models import Station


def test_build_feature_vector_success(db_session: Session, tenant_a):
    station = Station(tenant_id=tenant_a.id, code="ST1", name="Station 1")
    db_session.add(station)
    db_session.commit()

    pump = Pump(tenant_id=tenant_a.id, station_id=station.id, tag_number="PUMP-FE-01", status=PumpStatus.OPERATIONAL)
    db_session.add(pump)
    db_session.commit()

    vec = services.build_feature_vector(db_session, tenant_a.id, pump.id)
    assert isinstance(vec, dict)
    assert "vibration_axial_rolling_avg" in vec
    assert "health_deviation_index" in vec

    batch = services.build_feature_batch(db_session, tenant_a.id, [pump.id])
    assert pump.id in batch
    assert batch[pump.id] == vec
