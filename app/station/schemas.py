"""Pydantic v2 request/response models for the station module."""
import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict


class StationBase(BaseModel):
    code: str
    name: str
    region: str | None = None
    county: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    commissioned_on: date | None = None
    throughput_capacity_m3_per_day: float | None = None


class StationCreate(StationBase):
    pass


class StationUpdate(BaseModel):
    name: str | None = None
    region: str | None = None
    county: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    throughput_capacity_m3_per_day: float | None = None
    is_active: bool | None = None


class StationRead(StationBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    is_active: bool
