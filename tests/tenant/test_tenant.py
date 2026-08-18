"""Smoke tests for the tenant module."""
from sqlalchemy.orm import Session

from app.tenant import services
from app.tenant.schemas import TenantCreate


def test_router_registered():
    from app.main import app

    assert any(path.startswith("/api/v1/tenants") for path in app.openapi()["paths"])


def test_list_tenants_requires_auth(client):
    response = client.get("/api/v1/tenants")
    assert response.status_code == 401


def test_create_and_get_tenant(db_session: Session):
    tenant = services.create_tenant(
        db_session, TenantCreate(name="Acme Pipelines", slug="acme-pipelines")
    )
    assert tenant.id is not None
    assert tenant.is_active is True

    fetched = services.get_tenant(db_session, tenant.id)
    assert fetched is not None
    assert fetched.slug == "acme-pipelines"

    by_slug = services.get_tenant_by_slug(db_session, "acme-pipelines")
    assert by_slug is not None
    assert by_slug.id == tenant.id
