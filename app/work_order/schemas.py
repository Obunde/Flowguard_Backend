"""Pydantic v2 request/response models for the work_order module."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.work_order.models import WorkOrderSource, WorkOrderStatus


class WorkOrderBase(BaseModel):
    pump_id: uuid.UUID
    station_id: uuid.UUID
    title: str
    description: str | None = None
    priority: str = "normal"
    due_at: datetime | None = None


class WorkOrderCreate(WorkOrderBase):
    assigned_to_user_id: uuid.UUID | None = None
    source: WorkOrderSource = WorkOrderSource.MANUAL


class WorkOrderUpdate(BaseModel):
    status: WorkOrderStatus | None = None
    assigned_to_user_id: uuid.UUID | None = None
    priority: str | None = None
    due_at: datetime | None = None
    closed_at: datetime | None = None


class WorkOrderRead(WorkOrderBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    status: WorkOrderStatus
    source: WorkOrderSource
    created_by_user_id: uuid.UUID | None = None
    assigned_to_user_id: uuid.UUID | None = None
    closed_at: datetime | None = None
