from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base import Base

class GoldMLFeatures(Base):
    __tablename__ = "gold_ml_features"
    
    # We map a primary key purely for SQLAlchemy's internal object mapping
    id: Mapped[int] = mapped_column(primary_key=True)

    timestamp: Mapped[datetime] = mapped_column(DateTime)
    pump_id: Mapped[str] = mapped_column(String(50))
    vibration_axial_mm_s: Mapped[float] = mapped_column(Float)
    temperature_bearing_c: Mapped[float] = mapped_column(Float)
    pressure_discharge_psi: Mapped[float] = mapped_column(Float)
    
    # Rolling Averages
    rolling_3_avg_vib: Mapped[float] = mapped_column(Float)
    rolling_3_avg_temp: Mapped[float] = mapped_column(Float)
    
    rul_hours: Mapped[int] = mapped_column(Integer)
    failure_risk_7_day: Mapped[int] = mapped_column(Integer)