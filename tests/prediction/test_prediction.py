"""Smoke tests for the prediction module: router registration + tenant scoping."""
import uuid

from sqlalchemy.orm import Session

from app.prediction import services


def test_router_registered():
    from app.main import app

    assert any(path.startswith("/api/v1/predictions") for path in app.openapi()["paths"])


def test_list_requires_auth(client):
    response = client.get("/api/v1/predictions")
    assert response.status_code == 401


def test_list_is_tenant_scoped_and_empty_for_unknown_pump(db_session: Session, tenant_a):
    assert services.list_predictions(db_session, tenant_a.id) == []
    assert services.get_latest_prediction(db_session, tenant_a.id, uuid.uuid4()) is None


def test_run_prediction_success(db_session: Session, station_a):
    from app.pump.models import Pump, PumpStatus

    pump = Pump(
        tenant_id=station_a.tenant_id,
        station_id=station_a.id,
        tag_number="PS1-P01",
        status=PumpStatus.OPERATIONAL,
        prior_intervention_count=1,
    )
    db_session.add(pump)
    db_session.commit()
    db_session.refresh(pump)

    result = services.run_prediction(db_session, station_a.tenant_id, pump.id)
    assert result is not None
    assert result.pump_id == pump.id
    assert result.predicted_class in ["normal", "bearing_fault", "impeller_wear", "seal_leak"]
    assert 0.0 <= result.risk_score_7d <= 1.0
    assert result.model_version == "v1.0.0"

    latest = services.get_latest_prediction(db_session, station_a.tenant_id, pump.id)
    assert latest.id == result.id


def test_trigger_prediction_route(client, headers_a, station_a, db_session):
    from app.pump.models import Pump, PumpStatus

    pump = Pump(
        tenant_id=station_a.tenant_id,
        station_id=station_a.id,
        tag_number="PS1-P02",
        status=PumpStatus.OPERATIONAL,
    )
    db_session.add(pump)
    db_session.commit()

    trigger_res = client.post(f"/api/v1/predictions/pumps/{pump.id}/trigger", headers=headers_a)
    assert trigger_res.status_code == 201
    pred_data = trigger_res.json()
    assert pred_data["pump_id"] == str(pump.id)

    latest_res = client.get(f"/api/v1/predictions/pumps/{pump.id}/latest", headers=headers_a)
    assert latest_res.status_code == 200
    assert latest_res.json()["id"] == pred_data["id"]


def test_prediction_not_found_routes(client, headers_a):
    fake_id = "00000000-0000-0000-0000-000000000000"
    latest_res = client.get(
        f"/api/v1/predictions/pumps/{fake_id}/latest",
        headers=headers_a,
    )
    assert latest_res.status_code == 404
    trig_res = client.post(
        f"/api/v1/predictions/pumps/{fake_id}/trigger",
        headers=headers_a,
    )
    assert trig_res.status_code == 404

