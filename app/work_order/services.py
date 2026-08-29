"""Business logic for work orders."""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.prediction.services import get_latest_prediction, run_prediction
from app.pump.models import Pump
from app.work_order.models import WorkOrder, WorkOrderSource, WorkOrderStatus
from app.work_order.schemas import WorkOrderCreate, WorkOrderUpdate


def create_work_order(
    db: Session,
    tenant_id: uuid.UUID,
    payload: WorkOrderCreate,
    created_by_user_id: uuid.UUID | None = None,
) -> WorkOrder:
    work_order = WorkOrder(
        tenant_id=tenant_id, created_by_user_id=created_by_user_id, **payload.model_dump()
    )
    db.add(work_order)
    db.commit()
    db.refresh(work_order)
    return work_order


def get_work_order(
    db: Session, tenant_id: uuid.UUID, work_order_id: uuid.UUID
) -> WorkOrder | None:
    return db.scalar(
        select(WorkOrder).where(
            WorkOrder.id == work_order_id, WorkOrder.tenant_id == tenant_id
        )
    )


def list_work_orders(
    db: Session,
    tenant_id: uuid.UUID,
    status_filter: WorkOrderStatus | None = None,
    pump_id: uuid.UUID | None = None,
) -> list[WorkOrder]:
    stmt = select(WorkOrder).where(WorkOrder.tenant_id == tenant_id)
    if status_filter is not None:
        stmt = stmt.where(WorkOrder.status == status_filter)
    if pump_id is not None:
        stmt = stmt.where(WorkOrder.pump_id == pump_id)
    return list(db.scalars(stmt.order_by(WorkOrder.created_at.desc())))


def update_work_order(
    db: Session, tenant_id: uuid.UUID, work_order_id: uuid.UUID, payload: WorkOrderUpdate
) -> WorkOrder | None:
    work_order = get_work_order(db, tenant_id, work_order_id)
    if work_order is None:
        return None
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(work_order, field, value)
    db.commit()
    db.refresh(work_order)
    return work_order


def create_work_order_from_prediction(
    db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID
) -> WorkOrder | None:
    """Auto-generate a maintenance work order if latest 7-day failure risk score >= 0.70."""
    pump = db.scalar(select(Pump).where(Pump.id == pump_id, Pump.tenant_id == tenant_id))
    if pump is None:
        raise ValueError(f"Pump {pump_id} not found for tenant {tenant_id}")

    prediction = get_latest_prediction(db, tenant_id, pump_id)
    if prediction is None:
        prediction = run_prediction(db, tenant_id, pump_id)

    risk_score = float(prediction.risk_score_7d) if prediction.risk_score_7d is not None else 0.0
    if risk_score < 0.70 and prediction.predicted_class == "normal":
        return None

    priority = "high" if risk_score >= 0.85 else "normal"
    fault_label = prediction.predicted_class or "mechanical_anomaly"
    formatted_label = fault_label.replace("_", " ").title()
    title = f"Condition-Based Maintenance: {formatted_label} (Risk: {risk_score * 100:.1f}%)"
    description = (
        f"Automated work order raised from prediction scoring. "
        f"7-day failure risk score: {risk_score:.2f}, fault class: {fault_label}."
    )

    wo_create = WorkOrderCreate(
        pump_id=pump.id,
        station_id=pump.station_id,
        title=title,
        description=description,
        source=WorkOrderSource.ALERT,
        priority=priority,
    )
    return create_work_order(db, tenant_id, wo_create)
