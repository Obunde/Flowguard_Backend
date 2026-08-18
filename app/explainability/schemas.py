"""Pydantic v2 models for the explainability module."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FeatureAttributionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    pump_id: uuid.UUID
    computed_at: datetime
    component_scores: dict[str, float]
    shap_values: dict[str, float]
    top_component: str | None = None
    model_version: str | None = None
