"""Failure-risk service: a trained XGBoost classifier scores 7-day failure
probability; SHAP attribution picks the fault mode for scores above 0.35.
"""
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.feature_engineering.services import build_feature_vector
from app.ml.models import attribute, feature_row, get_bundle
from app.prediction.models import PredictionResult
from app.pump.models import Pump

NORMAL_THRESHOLD = 0.35
FAULT_CLASS_OF = {
    "bearing": "bearing_fault",
    "impeller": "impeller_wear",
    "seal": "seal_leak",
    "motor": "motor_fault",
}


def run_prediction(db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID) -> PredictionResult:
    """Score 7-day failure risk and classify the fault mode from SHAP attribution."""
    pump = db.scalar(select(Pump).where(Pump.id == pump_id, Pump.tenant_id == tenant_id))
    if pump is None:
        raise ValueError(f"Pump {pump_id} not found for tenant {tenant_id}")

    bundle = get_bundle()
    x = feature_row(build_feature_vector(db, tenant_id, pump_id))
    risk = round(min(1.0, max(0.0, float(bundle.risk.predict_proba(x)[0, 1]))), 4)

    if risk < NORMAL_THRESHOLD:
        predicted_class = "normal"
    else:
        _, _, top = attribute(bundle, x)
        predicted_class = FAULT_CLASS_OF[top]

    result = PredictionResult(
        tenant_id=tenant_id,
        pump_id=pump_id,
        computed_at=datetime.now(UTC),
        predicted_class=predicted_class,
        risk_score_7d=risk,
        model_version=bundle.version,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


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