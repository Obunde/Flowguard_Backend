"""Tenant management routes.

Cross-tenant by nature (creating/listing tenants), so these are gated by
role rather than by app.core.tenancy.get_current_tenant_id — see the note
in app/tenant/services.py. Routes only translate HTTP <-> services; no
business logic lives here.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import require_permission
from app.core.db import get_db
from app.core.permissions import Permission
from app.tenant import services
from app.tenant.schemas import TenantCreate, TenantRead, TenantUpdate

router = APIRouter(prefix="/api/v1/tenants", tags=["tenants"])


@router.post("", response_model=TenantRead, status_code=status.HTTP_201_CREATED)
def create_tenant(
    payload: TenantCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.MANAGE_TENANT)),
) -> TenantRead:
    return services.create_tenant(db, payload)


@router.get("", response_model=list[TenantRead])
def list_tenants(
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.MANAGE_TENANT)),
) -> list[TenantRead]:
    return services.list_tenants(db)


@router.get("/{tenant_id}", response_model=TenantRead)
def get_tenant(
    tenant_id: uuid.UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.MANAGE_TENANT)),
) -> TenantRead:
    tenant = services.get_tenant(db, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return tenant


@router.patch("/{tenant_id}", response_model=TenantRead)
def update_tenant(
    tenant_id: uuid.UUID,
    payload: TenantUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.MANAGE_TENANT)),
) -> TenantRead:
    tenant = services.update_tenant(db, tenant_id, payload)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return tenant
