"""Smoke tests for the model_metrics module: router registration + tenant scoping."""
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.model_metrics import services
from app.model_metrics.schemas import ModelMetricCreate


def test_router_registered():
    from app.main import app

    assert any(path.startswith("/api/v1/model-metrics") for path in app.openapi()["paths"])


def test_list_requires_auth(client):
    response = client.get("/api/v1/model-metrics")
    assert response.status_code == 401


def test_service_enforces_tenant_scope(db_session: Session, tenant_a, tenant_b):
    metric_a = services.record_metric(
        db_session,
        tenant_a.id,
        ModelMetricCreate(
            model_name="prediction-classifier",
            model_version="0.0.0-scaffold",
            metric_name="accuracy",
            metric_value=0.0,
            evaluated_at=datetime.now(UTC),
        ),
    )

    assert [m.id for m in services.list_metrics(db_session, tenant_a.id)] == [metric_a.id]
    assert services.list_metrics(db_session, tenant_b.id) == []
