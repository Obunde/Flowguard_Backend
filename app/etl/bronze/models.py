from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.core.base import Base # Assuming your Base declarative class is here

class BronzePumpTelemetry(Base):
    __tablename__ = "bronze_pump_telemetry"

    # SQLAlchemy requires a primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    pump_id: Mapped[str] = mapped_column(String(50), nullable=True)
    vibration_axial_mm_s: Mapped[float] = mapped_column(Float, nullable=True)
    vibration_radial_mm_s: Mapped[float] = mapped_column(Float, nullable=True)
    temperature_bearing_c: Mapped[float] = mapped_column(Float, nullable=True)
    temperature_casing_c: Mapped[float] = mapped_column(Float, nullable=True)
    pressure_suction_psi: Mapped[float] = mapped_column(Float, nullable=True)
    pressure_discharge_psi: Mapped[float] = mapped_column(Float, nullable=True)
    motor_current_amps: Mapped[float] = mapped_column(Float, nullable=True)
    motor_voltage_v: Mapped[float] = mapped_column(Float, nullable=True)
    rul_hours: Mapped[int] = mapped_column(Integer, nullable=True)
    failure_risk_7_day: Mapped[int] = mapped_column(Integer, nullable=True)
    ingestion_timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())