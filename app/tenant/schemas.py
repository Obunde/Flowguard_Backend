"""Pydantic v2 request/response models for the tenant module."""
import uuid

from pydantic import BaseModel, ConfigDict


class TenantBase(BaseModel):
    name: str
    slug: str
    fluid_type: str = "crude_oil"
    pressure_threshold_kpa: float = 0
    vibration_threshold_mm_s: float = 0
    branding_display_name: str | None = None
    branding_primary_color: str | None = None
    branding_logo_url: str | None = None


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: str | None = None
    fluid_type: str | None = None
    pressure_threshold_kpa: float | None = None
    vibration_threshold_mm_s: float | None = None
    branding_display_name: str | None = None
    branding_primary_color: str | None = None
    branding_logo_url: str | None = None
    is_active: bool | None = None


class TenantRead(TenantBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
