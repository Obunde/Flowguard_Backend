"""Pump routes. Thin: translate HTTP <-> services, no business logic."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.tenancy import get_current_tenant_id
from app.pump import services
from app.pump.schemas import PumpCreate, PumpRead, PumpUpdate

router = APIRouter(prefix="/api/v1/pumps", tags=["pumps"])


@router.post("", response_model=PumpRead, status_code=status.HTTP_201_CREATED)
def create_pump(
    payload: PumpCreate,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> PumpRead:
    return services.create_pump(db, tenant_id, payload)


@router.get("", response_model=list[PumpRead])
def list_pumps(
    station_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> list[PumpRead]:
    return services.list_pumps(db, tenant_id, station_id=station_id)


@router.get("/{pump_id}", response_model=PumpRead)
def get_pump(
    pump_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> PumpRead:
    pump = services.get_pump(db, tenant_id, pump_id)
    if pump is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pump not found")
    return pump


@router.patch("/{pump_id}", response_model=PumpRead)
def update_pump(
    pump_id: uuid.UUID,
    payload: PumpUpdate,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> PumpRead:
    pump = services.update_pump(db, tenant_id, pump_id, payload)
    if pump is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pump not found")
    return pump
