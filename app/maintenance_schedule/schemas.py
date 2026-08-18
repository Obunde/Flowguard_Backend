"""Pydantic v2 request/response models for the maintenance_schedule module."""
import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict

from app.maintenance_schedule.models import ScheduleStatus


class ScheduledMaintenanceCreate(BaseModel):
    pump_id: uuid.UUID
    station_id: uuid.UUID
    scheduled_date: date
    priority_rank: int | None = None
    created_from: str | None = None


class ScheduledMaintenanceUpdate(BaseModel):
    scheduled_date: date | None = None
    priority_rank: int | None = None
    status: ScheduleStatus | None = None
    work_order_id: uuid.UUID | None = None


class ScheduledMaintenanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    pump_id: uuid.UUID
    station_id: uuid.UUID
    work_order_id: uuid.UUID | None = None
    scheduled_date: date
    priority_rank: int | None = None
    status: ScheduleStatus
    created_from: str | None = None
