"""Smoke test for app.feature_engineering — services.py only, no HTTP surface."""
import uuid

import pytest
from sqlalchemy.orm import Session

from app.feature_engineering import services


def test_build_feature_vector_not_implemented(db_session: Session, tenant_a):
    with pytest.raises(NotImplementedError):
        services.build_feature_vector(db_session, tenant_a.id, uuid.uuid4())
