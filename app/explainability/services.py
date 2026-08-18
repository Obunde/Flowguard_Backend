"""Business logic for SHAP-based component attribution.

Computation logic is not implemented yet; reads of prior results are.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.explainability.models import FeatureAttribution


def compute_feature_attribution(
    db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID
) -> FeatureAttribution:
    """Run SHAP over the model used by app.prediction/app.rul for this pump
    and persist per-component attribution. Not implemented yet.
    """
    raise NotImplementedError("feature attribution computation is not implemented yet")


def get_latest_feature_attribution(
    db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID
) -> FeatureAttribution | None:
    stmt = (
        select(FeatureAttribution)
        .where(FeatureAttribution.tenant_id == tenant_id, FeatureAttribution.pump_id == pump_id)
        .order_by(FeatureAttribution.computed_at.desc())
        .limit(1)
    )
    return db.scalar(stmt)


def list_feature_attributions(
    db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID | None = None
) -> list[FeatureAttribution]:
    stmt = select(FeatureAttribution).where(FeatureAttribution.tenant_id == tenant_id)
    if pump_id is not None:
        stmt = stmt.where(FeatureAttribution.pump_id == pump_id)
    return list(db.scalars(stmt.order_by(FeatureAttribution.computed_at.desc())))
