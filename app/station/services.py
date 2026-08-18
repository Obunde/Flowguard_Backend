"""Business logic for stations.

Every function requires `tenant_id` explicitly and filters every query by
it — this is what makes cross-tenant queries structurally impossible from a
route. Routes never build their own queries; they call these functions.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.station.models import Station
from app.station.schemas import StationCreate, StationUpdate


def create_station(db: Session, tenant_id: uuid.UUID, payload: StationCreate) -> Station:
    station = Station(tenant_id=tenant_id, **payload.model_dump())
    db.add(station)
    db.commit()
    db.refresh(station)
    return station


def get_station(db: Session, tenant_id: uuid.UUID, station_id: uuid.UUID) -> Station | None:
    return db.scalar(
        select(Station).where(Station.id == station_id, Station.tenant_id == tenant_id)
    )


def list_stations(db: Session, tenant_id: uuid.UUID) -> list[Station]:
    return list(
        db.scalars(select(Station).where(Station.tenant_id == tenant_id).order_by(Station.code))
    )


def update_station(
    db: Session, tenant_id: uuid.UUID, station_id: uuid.UUID, payload: StationUpdate
) -> Station | None:
    station = get_station(db, tenant_id, station_id)
    if station is None:
        return None
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(station, field, value)
    db.commit()
    db.refresh(station)
    return station
