"""Business logic for RUL regression + MC Dropout confidence intervals.

Scoring logic is not implemented yet; reads of prior results are.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.rul.models import RulEstimate


def run_rul_estimate(db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID) -> RulEstimate:
    """Build a feature vector (app.feature_engineering), run the RUL
    regression model with MC Dropout sampling, and persist the result with
    confidence bounds. Not implemented yet.
    """
    raise NotImplementedError("RUL estimation is not implemented yet")


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
