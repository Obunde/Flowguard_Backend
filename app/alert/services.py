"""Business logic for alerts.

`create_alert`/read functions are implemented (plain persistence, not
"logic"). Deciding *when* to raise an alert from a Diagnostic result
(pressure residual, risk score, RUL) is threshold-evaluation logic that
belongs to a future `evaluate_thresholds`-style function — not implemented
yet.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.alert.models import Alert, AlertStatus
from app.alert.schemas import AlertCreate, AlertUpdate


def create_alert(db: Session, tenant_id: uuid.UUID, payload: AlertCreate) -> Alert:
    alert = Alert(tenant_id=tenant_id, **payload.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_alert(db: Session, tenant_id: uuid.UUID, alert_id: uuid.UUID) -> Alert | None:
    return db.scalar(select(Alert).where(Alert.id == alert_id, Alert.tenant_id == tenant_id))


def list_alerts(
    db: Session,
    tenant_id: uuid.UUID,
    status_filter: AlertStatus | None = None,
    pump_id: uuid.UUID | None = None,
) -> list[Alert]:
    stmt = select(Alert).where(Alert.tenant_id == tenant_id)
    if status_filter is not None:
        stmt = stmt.where(Alert.status == status_filter)
    if pump_id is not None:
        stmt = stmt.where(Alert.pump_id == pump_id)
    return list(db.scalars(stmt.order_by(Alert.triggered_at.desc())))


def update_alert(
    db: Session, tenant_id: uuid.UUID, alert_id: uuid.UUID, payload: AlertUpdate
) -> Alert | None:
    alert = get_alert(db, tenant_id, alert_id)
    if alert is None:
        return None
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(alert, field, value)
    db.commit()
    db.refresh(alert)
    return alert


def evaluate_thresholds(db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID) -> list[Alert]:
    """Compare the latest Flowgard/prediction/RUL results against the
    tenant's configured thresholds (app.tenant) and raise alerts as needed.
    Not implemented yet.
    """
    raise NotImplementedError("alert threshold evaluation is not implemented yet")
