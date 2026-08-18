"""Smoke tests for app.flowgard_engine — no routes.py by design (see module
docstring), so this only exercises the service layer directly.
"""
import uuid

import pytest
from sqlalchemy.orm import Session

from app.flowgard_engine import services


def test_list_is_tenant_scoped_and_empty_for_unknown_pump(db_session: Session, tenant_a):
    assert services.list_health_deviations(db_session, tenant_a.id) == []
    assert services.get_latest_health_deviation(db_session, tenant_a.id, uuid.uuid4()) is None


def test_compute_health_deviation_not_implemented(db_session: Session, tenant_a):
    with pytest.raises(NotImplementedError):
        services.compute_health_deviation(db_session, tenant_a.id, uuid.uuid4())
