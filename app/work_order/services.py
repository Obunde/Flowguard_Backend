"""Business logic for work orders."""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.work_order.models import WorkOrder, WorkOrderStatus
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
