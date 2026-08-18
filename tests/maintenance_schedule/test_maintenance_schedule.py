"""Smoke tests for the maintenance_schedule module: router registration + tenant scoping."""
from datetime import date, timedelta

import pytest
from sqlalchemy.orm import Session

from app.maintenance_schedule import services
from app.maintenance_schedule.schemas import ScheduledMaintenanceCreate
from app.pump.models import Pump, PumpStatus


def test_router_registered():
    from app.main import app

    assert any(path.startswith("/api/v1/maintenance-schedule") for path in app.openapi()["paths"])


def test_list_requires_auth(client):
    response = client.get("/api/v1/maintenance-schedule")
    assert response.status_code == 401


def test_service_enforces_tenant_scope(db_session: Session, station_a, station_b):
    pump_a = Pump(
        tenant_id=station_a.tenant_id,
        station_id=station_a.id,
        tag_number="PS1-P01",
        status=PumpStatus.OPERATIONAL,
    )
    db_session.add(pump_a)
    db_session.commit()
    db_session.refresh(pump_a)

    entry_a = services.create_scheduled_maintenance(
        db_session,
        station_a.tenant_id,
        ScheduledMaintenanceCreate(
            pump_id=pump_a.id,
            station_id=station_a.id,
            scheduled_date=date.today() + timedelta(days=14),
        ),
    )

    assert [e.id for e in services.list_scheduled_maintenance(db_session, station_a.tenant_id)] == [
        entry_a.id
    ]
    assert services.list_scheduled_maintenance(db_session, station_b.tenant_id) == []


def test_rank_schedule_by_rul_not_implemented(db_session: Session, tenant_a):
    with pytest.raises(NotImplementedError):
        services.rank_schedule_by_rul(db_session, tenant_a.id)
