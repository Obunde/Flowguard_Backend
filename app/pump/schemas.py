"""Pydantic v2 request/response models for the pump module."""
import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.pump.models import PumpStatus


class PumpBase(BaseModel):
    station_id: uuid.UUID
    tag_number: str
    manufacturer: str | None = None
    model_number: str | None = None
    install_date: date | None = None
    design_life_years: int | None = None
    last_overhaul_date: date | None = None
    prior_intervention_count: int = 0
    rated_flow_m3_per_hour: float | None = None
    rated_pressure_kpa: float | None = None
    commissioned_at: datetime | None = None


class PumpCreate(PumpBase):
    pass


class PumpUpdate(BaseModel):
    manufacturer: str | None = None
    model_number: str | None = None
    last_overhaul_date: date | None = None
    prior_intervention_count: int | None = None
    rated_flow_m3_per_hour: float | None = None
    rated_pressure_kpa: float | None = None
    status: PumpStatus | None = None


class PumpRead(PumpBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    status: PumpStatus
