"""Work order routes. Thin: translate HTTP <-> services, no business logic."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import CurrentUser, get_current_user
from app.core.db import get_db
from app.core.tenancy import get_current_tenant_id
from app.work_order import services
from app.work_order.models import WorkOrderStatus
from app.work_order.schemas import WorkOrderCreate, WorkOrderRead, WorkOrderUpdate

router = APIRouter(prefix="/api/v1/work-orders", tags=["work_orders"])


@router.post("", response_model=WorkOrderRead, status_code=status.HTTP_201_CREATED)
def create_work_order(
    payload: WorkOrderCreate,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: CurrentUser = Depends(get_current_user),
) -> WorkOrderRead:
    return services.create_work_order(db, tenant_id, payload, created_by_user_id=current_user.id)


@router.get("", response_model=list[WorkOrderRead])
def list_work_orders(
    status_filter: WorkOrderStatus | None = None,
    pump_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> list[WorkOrderRead]:
    return services.list_work_orders(db, tenant_id, status_filter=status_filter, pump_id=pump_id)


@router.get("/{work_order_id}", response_model=WorkOrderRead)
def get_work_order(
    work_order_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> WorkOrderRead:
    work_order = services.get_work_order(db, tenant_id, work_order_id)
    if work_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work order not found")
    return work_order


@router.patch("/{work_order_id}", response_model=WorkOrderRead)
def update_work_order(
    work_order_id: uuid.UUID,
    payload: WorkOrderUpdate,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> WorkOrderRead:
    work_order = services.update_work_order(db, tenant_id, work_order_id, payload)
    if work_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work order not found")
    return work_order


@router.post(
    "/auto-generate/pumps/{pump_id}",
    response_model=WorkOrderRead | None,
    status_code=status.HTTP_201_CREATED,
)
def auto_generate_work_order(
    pump_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> WorkOrderRead | None:
    try:
        wo = services.create_work_order_from_prediction(db, tenant_id, pump_id)
        if wo is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Risk score threshold not met for auto work order generation",
            )
        return wo
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err)) from err

