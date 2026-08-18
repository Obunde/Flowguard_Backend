"""Business logic for the Flowgard engine: pressure residual -> Health
Deviation Index. The core math is not implemented yet (this is what "we'll
fill in Flowgard math module by module" refers to); read access to prior
results is implemented since app.prediction/app.alert will need it.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.flowgard_engine.models import HealthDeviationRecord


def compute_health_deviation(
    db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID
) -> HealthDeviationRecord:
    """Compute pressure residual from the latest feature vector
    (app.feature_engineering) and derive the Health Deviation Index. Not
    implemented yet.
    """
    raise NotImplementedError("Flowgard health deviation computation is not implemented yet")


def get_latest_health_deviation(
    db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID
) -> HealthDeviationRecord | None:
    stmt = (
        select(HealthDeviationRecord)
        .where(
            HealthDeviationRecord.tenant_id == tenant_id,
            HealthDeviationRecord.pump_id == pump_id,
        )
        .order_by(HealthDeviationRecord.computed_at.desc())
        .limit(1)
    )
    return db.scalar(stmt)


def list_health_deviations(
    db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID | None = None
) -> list[HealthDeviationRecord]:
    stmt = select(HealthDeviationRecord).where(HealthDeviationRecord.tenant_id == tenant_id)
    if pump_id is not None:
        stmt = stmt.where(HealthDeviationRecord.pump_id == pump_id)
    return list(db.scalars(stmt.order_by(HealthDeviationRecord.computed_at.desc())))
