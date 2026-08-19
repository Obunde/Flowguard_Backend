from sqlalchemy import select
from sqlalchemy.orm import Session
from app.etl.bronze.models import BronzePumpTelemetry

def ingest_telemetry_reading(session: Session, reading_data: dict) -> BronzePumpTelemetry:
    """Inserts a single raw sensor reading into the Bronze storage."""
    new_reading = BronzePumpTelemetry(**reading_data)
    session.add(new_reading)
    session.commit()
    session.refresh(new_reading)
    return new_reading

def get_raw_telemetry(session: Session, pump_id: str, limit: int = 100):
    """Retrieves the most recent raw telemetry data for a specific pump."""
    stmt = select(BronzePumpTelemetry).where(
        BronzePumpTelemetry.pump_id == pump_id
    ).order_by(BronzePumpTelemetry.timestamp.desc()).limit(limit)
    
    return session.scalars(stmt).all()