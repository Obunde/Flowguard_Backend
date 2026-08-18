"""Business logic for tenant management.

Deliberately NOT tenant-scoped by tenant_id (a tenant can't scope itself) —
these functions are reached only through admin-role-gated routes. Every
other module's services.py takes `tenant_id` as an explicit argument; this
one is the root of that chain.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.tenant.models import Tenant
from app.tenant.schemas import TenantCreate, TenantUpdate


def create_tenant(db: Session, payload: TenantCreate) -> Tenant:
    tenant = Tenant(**payload.model_dump())
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


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
