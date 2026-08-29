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


def test_create_and_get_pump_route(client, headers_a, station_a):
    payload = {
        "station_id": str(station_a.id),
        "tag_number": "PS1-P02",
        "manufacturer": "Sulzer",
        "model_number": "MSD 8x10",
        "rated_flow_m3_per_hour": 850.0,
        "rated_pressure_kpa": 4500.0,
    }
    res = client.post("/api/v1/pumps", json=payload, headers=headers_a)
    assert res.status_code == 201
    pump_id = res.json()["id"]

    get_res = client.get(f"/api/v1/pumps/{pump_id}", headers=headers_a)
    assert get_res.status_code == 200
    assert get_res.json()["tag_number"] == "PS1-P02"
    assert get_res.json()["status"] == "operational"


def test_pump_filtering_and_not_found(client, headers_a, station_a):
    fake_id = "00000000-0000-0000-0000-000000000000"
    assert client.get(f"/api/v1/pumps/{fake_id}", headers=headers_a).status_code == 404
    patch_res = client.patch(
        f"/api/v1/pumps/{fake_id}",
        json={"status": "maintenance"},
        headers=headers_a,
    )
    assert patch_res.status_code == 404

    # Filter by station_id
    res = client.get(f"/api/v1/pumps?station_id={station_a.id}", headers=headers_a)
    assert res.status_code == 200


def test_update_pump_route(client, headers_a, station_a):
    payload = {
        "station_id": str(station_a.id),
        "tag_number": "PS1-P03",
        "manufacturer": "KSB",
    }
    create_res = client.post("/api/v1/pumps", json=payload, headers=headers_a)
    pump_id = create_res.json()["id"]

    patch_res = client.patch(
        f"/api/v1/pumps/{pump_id}",
        json={"status": "maintenance", "prior_intervention_count": 2},
        headers=headers_a,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "maintenance"

