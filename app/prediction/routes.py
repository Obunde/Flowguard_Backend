"""Prediction routes. Thin: translate HTTP <-> services, no business logic."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.tenancy import get_current_tenant_id
from app.prediction import services
from app.prediction.schemas import PredictionResultRead

router = APIRouter(prefix="/api/v1/predictions", tags=["predictions"])


@router.get("", response_model=list[PredictionResultRead])
def list_predictions(
    pump_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> list[PredictionResultRead]:
    return services.list_predictions(db, tenant_id, pump_id=pump_id)


@router.get("/pumps/{pump_id}/latest", response_model=PredictionResultRead)
def get_latest_prediction(
    pump_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> PredictionResultRead:
    result = services.get_latest_prediction(db, tenant_id, pump_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No prediction found")
    return result
