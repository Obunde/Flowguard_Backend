"""Tenant management routes.

Cross-tenant by nature (creating/listing tenants), so these are gated on the
PLATFORM_ADMIN role rather than by app.core.tenancy.get_current_tenant_id
(a tenant admin may also read/update their own tenant's settings) —
see the note in app/tenant/services.py. Routes only translate HTTP <->
services; no business logic lives here.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import CurrentUser, get_current_user, require_role
from app.core.db import get_db
from app.core.email import EmailNotConfiguredError
from app.core.permissions import Permission, has_permission
from app.tenant import services
from app.tenant.schemas import TenantCreate, TenantOnboardRead, TenantRead, TenantUpdate

router = APIRouter(prefix="/api/v1/tenants", tags=["tenants"])

def require_platform_admin(
    current_user: CurrentUser = Depends(require_role("platform_admin")),
) -> CurrentUser:
    """platform_admin AND tenant-less — a tenant-bound user with this role
    claim (e.g. one minted before the schema check) is refused."""
    if current_user.tenant_id is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user


def require_tenant_access(
    tenant_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """The tenant-less platform admin may manage any tenant; otherwise the
    caller needs MANAGE_TENANT and may only touch their own tenant."""
    if current_user.role == "platform_admin" and current_user.tenant_id is None:
        return current_user
    if not has_permission(current_user.role, Permission.MANAGE_TENANT) or current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant access denied")
    return current_user


@router.post("", response_model=TenantOnboardRead, status_code=status.HTTP_201_CREATED)
def onboard_tenant(
    payload: TenantCreate,
    db: Session = Depends(get_db),
    _=Depends(require_platform_admin),
) -> TenantOnboardRead:
    try:
        tenant, admin = services.onboard_tenant(db, payload)
    except EmailNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Tenant created but the admin invite email could not be sent: "
            "SMTP is not configured",
        ) from exc
    return TenantOnboardRead(
        **TenantRead.model_validate(tenant).model_dump(),
        admin_user_id=admin.id,
        admin_email=admin.email,
    )


@router.get("", response_model=list[TenantRead])
def list_tenants(
    db: Session = Depends(get_db),
    _=Depends(require_platform_admin),
) -> list[TenantRead]:
    return services.list_tenants(db)


@router.get("/{tenant_id}", response_model=TenantRead)
def get_tenant(
    tenant_id: uuid.UUID,
    db: Session = Depends(get_db),
    _=Depends(require_tenant_access),
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
    _=Depends(require_tenant_access),
) -> TenantRead:
    tenant = services.update_tenant(db, tenant_id, payload)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return tenant
