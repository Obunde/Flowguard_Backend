"""Business logic for RUL quantile regression + 90% confidence intervals."""
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.feature_engineering.services import build_feature_vector
from app.ml.models import feature_row, get_bundle
from app.pump.models import Pump
from app.rul.models import RulEstimate


def run_rul_estimate(db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID) -> RulEstimate:
    """Predict remaining useful life with 5th/50th/95th percentile quantile
    regressors (XGBoost). Bounds are the 90% interval; `mc_dropout_samples`
    is left unset because no MC Dropout model is used.
    """
    pump = db.scalar(select(Pump).where(Pump.id == pump_id, Pump.tenant_id == tenant_id))
    if pump is None:
        raise ValueError(f"Pump {pump_id} not found for tenant {tenant_id}")

    bundle = get_bundle()
    x = feature_row(build_feature_vector(db, tenant_id, pump_id))
    lo, mid, hi = (
        float(bundle.rul[q].predict(x)[0]) for q in (0.05, 0.5, 0.95)
    )
    # Quantile heads are trained independently and can cross; order them.
    lo, mid, hi = sorted((lo, mid, hi))
    to_days = lambda hours: round(max(0.0, hours) / 24.0, 2)  # noqa: E731

    estimate = RulEstimate(
        tenant_id=tenant_id,
        pump_id=pump_id,
        computed_at=datetime.now(UTC),
        remaining_useful_life_days=to_days(mid),
        confidence_lower_days=to_days(lo),
        confidence_upper_days=to_days(hi),
        mc_dropout_samples=None,
        model_version=bundle.version,
    )
    db.add(estimate)
    db.commit()
    db.refresh(estimate)
    return estimate


def get_latest_rul_estimate(
    db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID
) -> RulEstimate | None:
    stmt = (
        select(RulEstimate)
        .where(RulEstimate.tenant_id == tenant_id, RulEstimate.pump_id == pump_id)
        .order_by(RulEstimate.computed_at.desc())
        .limit(1)
    )
    return db.scalar(stmt)


def list_rul_estimates(
    db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID | None = None
) -> list[RulEstimate]:
    stmt = select(RulEstimate).where(RulEstimate.tenant_id == tenant_id)
    if pump_id is not None:
        stmt = stmt.where(RulEstimate.pump_id == pump_id)
    return list(db.scalars(stmt.order_by(RulEstimate.computed_at.desc())))
