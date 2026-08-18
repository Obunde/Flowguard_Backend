"""Smoke tests for the work_order module: router registration + tenant scoping."""
from sqlalchemy.orm import Session

from app.pump.models import Pump, PumpStatus
from app.work_order import services
from app.work_order.schemas import WorkOrderCreate


def test_router_registered():
    from app.main import app

    assert any(path.startswith("/api/v1/work-orders") for path in app.openapi()["paths"])


def test_list_work_orders_requires_auth(client):
    response = client.get("/api/v1/work-orders")
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

    wo_a = services.create_work_order(
        db_session,
        station_a.tenant_id,
        WorkOrderCreate(pump_id=pump_a.id, station_id=station_a.id, title="Inspect seal"),
    )

    assert [w.id for w in services.list_work_orders(db_session, station_a.tenant_id)] == [wo_a.id]
    assert services.list_work_orders(db_session, station_b.tenant_id) == []
    assert services.get_work_order(db_session, station_b.tenant_id, wo_a.id) is None
