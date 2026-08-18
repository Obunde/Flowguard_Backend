"""Smoke tests for the pump module: router registration + tenant scoping."""
from sqlalchemy.orm import Session

from app.pump import services
from app.pump.models import Pump, PumpStatus


def test_router_registered():
    from app.main import app

    assert any(path.startswith("/api/v1/pumps") for path in app.openapi()["paths"])


def test_list_pumps_requires_auth(client):
    response = client.get("/api/v1/pumps")
    assert response.status_code == 401


def test_service_enforces_tenant_scope(db_session: Session, station_a, station_b):
    pump_a = Pump(
        tenant_id=station_a.tenant_id,
        station_id=station_a.id,
        tag_number="PS1-P01",
        status=PumpStatus.OPERATIONAL,
    )
    pump_b = Pump(
        tenant_id=station_b.tenant_id,
        station_id=station_b.id,
        tag_number="PS1-P01",
        status=PumpStatus.OPERATIONAL,
    )
    db_session.add_all([pump_a, pump_b])
    db_session.commit()

    pumps_for_a = services.list_pumps(db_session, station_a.tenant_id)
    assert [p.id for p in pumps_for_a] == [pump_a.id]

    # Same tag_number exists in both tenants — fetching tenant B's pump id
    # under tenant A's context must return nothing.
    assert services.get_pump(db_session, station_a.tenant_id, pump_b.id) is None
