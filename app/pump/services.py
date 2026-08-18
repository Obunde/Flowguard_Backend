"""Business logic for pumps. Same tenant-scoping discipline as app/station."""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.pump.models import Pump
from app.pump.schemas import PumpCreate, PumpUpdate


def create_pump(db: Session, tenant_id: uuid.UUID, payload: PumpCreate) -> Pump:
    pump = Pump(tenant_id=tenant_id, **payload.model_dump())
    db.add(pump)
    db.commit()
    db.refresh(pump)
    return pump


def get_pump(db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID) -> Pump | None:
    return db.scalar(select(Pump).where(Pump.id == pump_id, Pump.tenant_id == tenant_id))


def list_pumps(
    db: Session, tenant_id: uuid.UUID, station_id: uuid.UUID | None = None
) -> list[Pump]:
    stmt = select(Pump).where(Pump.tenant_id == tenant_id)
    if station_id is not None:
        stmt = stmt.where(Pump.station_id == station_id)
    return list(db.scalars(stmt.order_by(Pump.tag_number)))


def update_pump(
    db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID, payload: PumpUpdate
) -> Pump | None:
    pump = get_pump(db, tenant_id, pump_id)
    if pump is None:
        return None
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(pump, field, value)
    db.commit()
    db.refresh(pump)
    return pump
