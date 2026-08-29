"""Smoke tests for the explainability module: router registration + tenant scoping."""
import uuid

import pytest
from sqlalchemy.orm import Session

from app.explainability import services


def test_router_registered():
    from app.main import app

    assert any(path.startswith("/api/v1/explainability") for path in app.openapi()["paths"])


def test_list_requires_auth(client):
    response = client.get("/api/v1/explainability")
    assert response.status_code == 401


def test_list_is_tenant_scoped_and_empty_for_unknown_pump(db_session: Session, tenant_a):
    assert services.list_feature_attributions(db_session, tenant_a.id) == []
    assert services.get_latest_feature_attribution(db_session, tenant_a.id, uuid.uuid4()) is None


def test_compute_feature_attribution_success(db_session: Session, station_a):
    from app.pump.models import Pump, PumpStatus

    pump = Pump(
        tenant_id=station_a.tenant_id,
        station_id=station_a.id,
        tag_number="PS1-P01",
        status=PumpStatus.OPERATIONAL,
    )
    db_session.add(pump)
    db_session.commit()

    attribution = services.compute_feature_attribution(db_session, station_a.tenant_id, pump.id)
    assert attribution is not None
    assert attribution.pump_id == pump.id
    assert attribution.top_component in ["bearing", "impeller", "seal", "motor"]
    assert "vibration_mean" in attribution.shap_values
    assert "bearing" in attribution.component_scores

    latest = services.get_latest_feature_attribution(db_session, station_a.tenant_id, pump.id)
    assert latest.id == attribution.id


def test_trigger_explainability_route(client, headers_a, station_a, db_session):
    from app.pump.models import Pump, PumpStatus

    pump = Pump(
        tenant_id=station_a.tenant_id,
        station_id=station_a.id,
        tag_number="PS1-P02",
        status=PumpStatus.OPERATIONAL,
    )
    db_session.add(pump)
    db_session.commit()

    trigger_res = client.post(f"/api/v1/explainability/pumps/{pump.id}/trigger", headers=headers_a)
    assert trigger_res.status_code == 201
    attr_data = trigger_res.json()
    assert attr_data["pump_id"] == str(pump.id)

    latest_res = client.get(f"/api/v1/explainability/pumps/{pump.id}/latest", headers=headers_a)
    assert latest_res.status_code == 200
    assert latest_res.json()["id"] == attr_data["id"]


def test_explainability_not_found_routes(client, headers_a):
    fake_id = "00000000-0000-0000-0000-000000000000"
    assert client.get(f"/api/v1/explainability/pumps/{fake_id}/latest", headers=headers_a).status_code == 404
    assert client.post(f"/api/v1/explainability/pumps/{fake_id}/trigger", headers=headers_a).status_code == 404

