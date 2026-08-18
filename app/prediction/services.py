"""Business logic for the classification model + 7-day risk score.

Scoring logic is not implemented yet; reads of prior results are.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.prediction.models import PredictionResult


def run_prediction(db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID) -> PredictionResult:
    """Build a feature vector (app.feature_engineering), run the
    classification model, and persist the result. Not implemented yet.
    """
    raise NotImplementedError("prediction scoring is not implemented yet")


def get_latest_prediction(
    db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID
) -> PredictionResult | None:
    stmt = (
        select(PredictionResult)
        .where(PredictionResult.tenant_id == tenant_id, PredictionResult.pump_id == pump_id)
        .order_by(PredictionResult.computed_at.desc())
        .limit(1)
    )
    return db.scalar(stmt)


def list_predictions(
    db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID | None = None
) -> list[PredictionResult]:
    stmt = select(PredictionResult).where(PredictionResult.tenant_id == tenant_id)
    if pump_id is not None:
        stmt = stmt.where(PredictionResult.pump_id == pump_id)
    return list(db.scalars(stmt.order_by(PredictionResult.computed_at.desc())))
