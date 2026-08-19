from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base import Base

class SilverPumpTelemetry(Base):
    __tablename__ = "silver_pump_telemetry"
    # Note: Alembic/SQLAlchemy shouldn't generate migration scripts for this automatically.
    # The view creation requires raw SQL in your migration files.

    # We map a primary key purely for SQLAlchemy's internal object mapping
    id: Mapped[int] = mapped_column(primary_key=True) 
    
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    pump_id: Mapped[str] = mapped_column(String(50))
    vibration_axial_mm_s: Mapped[float] = mapped_column(Float)
    vibration_radial_mm_s: Mapped[float] = mapped_column(Float)
    temperature_bearing_c: Mapped[float] = mapped_column(Float)
    temperature_casing_c: Mapped[float] = mapped_column(Float)
    pressure_suction_psi: Mapped[float] = mapped_column(Float)
    pressure_discharge_psi: Mapped[float] = mapped_column(Float)
    motor_current_amps: Mapped[float] = mapped_column(Float)
    motor_voltage_v: Mapped[float] = mapped_column(Float)
    rul_hours: Mapped[int] = mapped_column(Integer)
    failure_risk_7_day: Mapped[int] = mapped_column(Integer)