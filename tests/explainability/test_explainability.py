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


def test_compute_feature_attribution_not_implemented(db_session: Session, tenant_a):
    with pytest.raises(NotImplementedError):
        services.compute_feature_attribution(db_session, tenant_a.id, uuid.uuid4())
