"""Pydantic v2 models for the rul module."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RulEstimateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    pump_id: uuid.UUID
    computed_at: datetime
    remaining_useful_life_days: float | None = None
    confidence_lower_days: float | None = None
    confidence_upper_days: float | None = None
    mc_dropout_samples: int | None = None
    model_version: str | None = None
