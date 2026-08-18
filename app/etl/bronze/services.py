"""Bronze-layer landing. Append-only, minimal validation — so this is safe
to implement fully even though downstream transform logic (silver/gold) is
still a stub: landing a raw event is not a business decision.
"""
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.etl.bronze.models import BronzeEvent, BronzeStream


def land_event(
    db: Session,
    tenant_id: uuid.UUID,
    stream: BronzeStream,
    payload: dict,
    recorded_at: datetime,
    source_ref_id: uuid.UUID | None = None,
) -> BronzeEvent:
    event = BronzeEvent(
        tenant_id=tenant_id,
        stream=stream,
        payload=payload,
        recorded_at=recorded_at,
        source_ref_id=source_ref_id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_unprocessed_events(
    db: Session, tenant_id: uuid.UUID, stream: BronzeStream, limit: int = 500
) -> list[BronzeEvent]:
    """Read side used by silver-layer jobs. "Unprocessed" bookkeeping
    (watermarks/cursors) is part of the silver conforming logic and is not
    implemented yet — this currently just returns the most recent events.
    """
    stmt = (
        select(BronzeEvent)
        .where(BronzeEvent.tenant_id == tenant_id, BronzeEvent.stream == stream)
        .order_by(BronzeEvent.recorded_at.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt))
