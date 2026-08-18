"""Pydantic v2 models for the flowgard_engine module."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HealthDeviationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    pump_id: uuid.UUID
    computed_at: datetime
    pressure_residual: float | None = None
    health_deviation_index: float | None = None
