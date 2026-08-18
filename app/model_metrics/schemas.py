"""Pydantic v2 request/response models for the model_metrics module."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ModelMetricCreate(BaseModel):
    model_name: str
    model_version: str
    dataset_split: str | None = None
    metric_name: str
    metric_value: float
    confusion_matrix: dict | None = None
    evaluated_at: datetime


class ModelMetricRead(ModelMetricCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
