"""Tenant management. Not tenant-scoped (a tenant can't scope itself); gated
on the platform_admin role. `onboard_tenant` also creates the tenant's first
ADMIN via app.user.services.onboard_user.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.tenant.models import Tenant
from app.tenant.schemas import TenantCreate, TenantUpdate
from app.user import services as user_services
from app.user.models import User, UserRole
from app.user.schemas import UserCreate

_TENANT_FIELDS = (
    "name",
    "slug",
    "fluid_type",
    "pressure_threshold_kpa",
    "vibration_threshold_mm_s",
    "branding_display_name",
    "branding_primary_color",
    "branding_logo_url",
)


def onboard_tenant(db: Session, payload: TenantCreate) -> tuple[Tenant, User]:
    """Create the tenant and its first ADMIN (emailed a first-time password)."""
    tenant = Tenant(**{field: getattr(payload, field) for field in _TENANT_FIELDS})
    db.add(tenant)
    db.flush()  # assign tenant.id

    admin = user_services.onboard_user(
        db,
        tenant.id,
        UserCreate(
            email=payload.admin_email,
            full_name=payload.admin_full_name,
            role=UserRole.ADMIN,
        ),
        context=(
            f"You have been set up as the administrator for the '{tenant.name}' "
            f"workspace on Flowgard."
        ),
    )
    db.refresh(tenant)
    return tenant, admin


def get_tenant(db: Session, tenant_id: uuid.UUID) -> Tenant | None:
    return db.get(Tenant, tenant_id)


def get_tenant_by_slug(db: Session, slug: str) -> Tenant | None:
    return db.scalar(select(Tenant).where(Tenant.slug == slug))


def list_tenants(db: Session) -> list[Tenant]:
    return list(db.scalars(select(Tenant).order_by(Tenant.name)))


def update_tenant(db: Session, tenant_id: uuid.UUID, payload: TenantUpdate) -> Tenant | None:
    tenant = get_tenant(db, tenant_id)
    if tenant is None:
        return None
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(tenant, field, value)
    db.commit()
    db.refresh(tenant)
    return tenant
