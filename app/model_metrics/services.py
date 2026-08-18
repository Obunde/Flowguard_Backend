"""Business logic for recording/reading model performance metrics.

Recording a metric is plain persistence and is implemented; computing
metrics from an evaluation run (benchmarking a model against a held-out
set) belongs to app.prediction/app.rul and is not implemented yet.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model_metrics.models import ModelMetric
from app.model_metrics.schemas import ModelMetricCreate


def record_metric(db: Session, tenant_id: uuid.UUID, payload: ModelMetricCreate) -> ModelMetric:
    metric = ModelMetric(tenant_id=tenant_id, **payload.model_dump())
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


def list_metrics(
    db: Session,
    tenant_id: uuid.UUID,
    model_name: str | None = None,
    model_version: str | None = None,
) -> list[ModelMetric]:
    stmt = select(ModelMetric).where(ModelMetric.tenant_id == tenant_id)
    if model_name is not None:
        stmt = stmt.where(ModelMetric.model_name == model_name)
    if model_version is not None:
        stmt = stmt.where(ModelMetric.model_version == model_version)
    return list(db.scalars(stmt.order_by(ModelMetric.evaluated_at.desc())))
