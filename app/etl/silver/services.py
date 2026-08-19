from sqlalchemy import select
from sqlalchemy.orm import Session
from app.etl.silver.models import SilverPumpTelemetry

def get_cleaned_telemetry(session: Session, pump_id: str, limit: int = 100):
    """Retrieves validated, real-time telemetry from the Silver view."""
    stmt = select(SilverPumpTelemetry).where(
        SilverPumpTelemetry.pump_id == pump_id
    ).order_by(SilverPumpTelemetry.timestamp.desc()).limit(limit)
    
    return session.scalars(stmt).all()