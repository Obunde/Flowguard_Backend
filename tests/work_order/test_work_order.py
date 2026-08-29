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


def test_work_order_routes_crud(client, headers_a, station_a, db_session):
    pump_a = Pump(
        tenant_id=station_a.tenant_id,
        station_id=station_a.id,
        tag_number="PS1-P02",
        status=PumpStatus.OPERATIONAL,
    )
    db_session.add(pump_a)
    db_session.commit()

    payload = {
        "pump_id": str(pump_a.id),
        "station_id": str(station_a.id),
        "title": "Replace mechanical seal",
        "priority": "high",
    }
    create_res = client.post("/api/v1/work-orders", json=payload, headers=headers_a)
    assert create_res.status_code == 201
    wo_id = create_res.json()["id"]

    get_res = client.get(f"/api/v1/work-orders/{wo_id}", headers=headers_a)
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Replace mechanical seal"

    patch_res = client.patch(f"/api/v1/work-orders/{wo_id}", json={"status": "in_progress"}, headers=headers_a)
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "in_progress"


def test_auto_generate_work_order_route(client, headers_a, station_a, db_session):
    from datetime import datetime, timezone
    from app.prediction.models import PredictionResult

    pump_a = Pump(
        tenant_id=station_a.tenant_id,
        station_id=station_a.id,
        tag_number="PS1-P03",
        status=PumpStatus.OPERATIONAL,
        prior_intervention_count=5,
    )
    db_session.add(pump_a)
    db_session.commit()

    pred = PredictionResult(
        tenant_id=station_a.tenant_id,
        pump_id=pump_a.id,
        computed_at=datetime.now(timezone.utc),
        predicted_class="bearing_fault",
        risk_score_7d=0.88,
        model_version="v1.0.0",
    )
    db_session.add(pred)
    db_session.commit()

    auto_res = client.post(f"/api/v1/work-orders/auto-generate/pumps/{pump_a.id}", headers=headers_a)
    assert auto_res.status_code == 201
    wo_data = auto_res.json()
    assert wo_data["pump_id"] == str(pump_a.id)
    assert wo_data["source"] == "alert"


def test_work_order_not_found(client, headers_a):
    fake_id = "00000000-0000-0000-0000-000000000000"
    assert client.get(f"/api/v1/work-orders/{fake_id}", headers=headers_a).status_code == 404
    assert client.patch(f"/api/v1/work-orders/{fake_id}", json={"status": "completed"}, headers=headers_a).status_code == 404

