"""Smoke tests for the station module: router registration + tenant scoping."""
from sqlalchemy.orm import Session

from app.station import services


def test_router_registered():
    from app.main import app

    assert any(path.startswith("/api/v1/stations") for path in app.openapi()["paths"])


def test_list_stations_requires_auth(client):
    response = client.get("/api/v1/stations")
    assert response.status_code == 401


def test_service_enforces_tenant_scope(db_session: Session, station_a, station_b):
    stations_for_a = services.list_stations(db_session, station_a.tenant_id)
    stations_for_b = services.list_stations(db_session, station_b.tenant_id)

    assert [s.id for s in stations_for_a] == [station_a.id]
    assert [s.id for s in stations_for_b] == [station_b.id]

    # Querying tenant A's data with tenant B's id must not find it.
    assert services.get_station(db_session, station_b.tenant_id, station_a.id) is None


def test_service_requires_tenant_id_argument():
    # tenant_id is a mandatory positional/keyword argument on every
    # tenant-scoped service function — calling without it is a TypeError,
    # not a silent cross-tenant query.
    import inspect

    sig = inspect.signature(services.list_stations)
    assert "tenant_id" in sig.parameters
    assert sig.parameters["tenant_id"].default is inspect.Parameter.empty


def test_route_returns_only_own_tenant_stations(client, headers_a, headers_b, station_a, station_b):
    response_a = client.get("/api/v1/stations", headers=headers_a)
    assert response_a.status_code == 200
    assert [s["id"] for s in response_a.json()] == [str(station_a.id)]

    response_b = client.get("/api/v1/stations", headers=headers_b)
    assert response_b.status_code == 200
    assert [s["id"] for s in response_b.json()] == [str(station_b.id)]
