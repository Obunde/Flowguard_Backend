"""App-wide smoke tests: every module router is registered, health check works."""
from fastapi.testclient import TestClient

EXPECTED_PREFIXES = [
    "/api/v1/tenants",
    "/api/v1/stations",
    "/api/v1/pumps",
    "/api/v1/users",
    "/api/v1/work-orders",
    "/api/v1/predictions",
    "/api/v1/rul",
    "/api/v1/explainability",
    "/api/v1/alerts",
    "/api/v1/maintenance-schedule",
    "/api/v1/model-metrics",
]


def test_all_module_routers_registered():
    from app.main import app

    # Route registration is checked via the resolved OpenAPI schema rather
    # than `app.routes` directly: FastAPI may represent an included router
    # as an opaque lazy wrapper there, but `.openapi()` always resolves to
    # the concrete path list, so this stays correct across FastAPI versions.
    paths = list(app.openapi()["paths"].keys())
    for prefix in EXPECTED_PREFIXES:
        assert any(path.startswith(prefix) for path in paths), f"no route registered under {prefix}"


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app"] == "flowgard"
