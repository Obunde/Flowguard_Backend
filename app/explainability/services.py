"""Business logic for SHAP-based component attribution.

Computation logic is not implemented yet; reads of prior results are.
"""
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.explainability.models import FeatureAttribution
from app.feature_engineering.services import build_feature_vector
from app.ml.models import attribute, feature_row, get_bundle
from app.pump.models import Pump


def compute_feature_attribution(
    db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID
) -> FeatureAttribution:
    """Per-feature SHAP values from the failure-risk model, rolled up into
    sub-assembly shares (bearing / impeller / seal / motor)."""
    pump = db.scalar(select(Pump).where(Pump.id == pump_id, Pump.tenant_id == tenant_id))
    if pump is None:
        raise ValueError(f"Pump {pump_id} not found for tenant {tenant_id}")

    bundle = get_bundle()
    x = feature_row(build_feature_vector(db, tenant_id, pump_id))
    per_feature, shares, top = attribute(bundle, x)

    attribution = FeatureAttribution(
        tenant_id=tenant_id,
        pump_id=pump_id,
        computed_at=datetime.now(UTC),
        component_scores=shares,
        shap_values={k: round(v, 6) for k, v in per_feature.items()},
        top_component=top,
        model_version=bundle.version,
    )
    db.add(attribution)
    db.commit()
    db.refresh(attribution)
    return attribution


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