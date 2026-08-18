"""Reads Gold-layer tables (app.etl.gold), produces model-ready feature
vectors for prediction / rul / flowgard_engine / explainability.

No models.py/routes.py/schemas.py here by design — this module has no
tables of its own and no HTTP surface; it's a pure read+transform layer
sitting between ETL and the modelling modules. Feature computation logic is
not implemented yet.
"""
import uuid

from sqlalchemy.orm import Session

# Deliberately imported at call sites within these functions once
# implemented (e.g. `gold_services.list_pump_feature_windows`), not at
# module scope, to keep this stub importable without unused-import noise.


def build_feature_vector(db: Session, tenant_id: uuid.UUID, pump_id: uuid.UUID) -> dict[str, float]:
    """Assemble the latest model-ready feature vector for one pump from
    Gold-layer rolling-window features. Not implemented yet.
    """
    raise NotImplementedError("feature vector construction is not implemented yet")


def build_feature_batch(
    db: Session, tenant_id: uuid.UUID, pump_ids: list[uuid.UUID]
) -> dict[uuid.UUID, dict[str, float]]:
    """Batch version of `build_feature_vector`, used by scheduled scoring
    runs across a tenant's fleet. Not implemented yet.
    """
    raise NotImplementedError("batch feature vector construction is not implemented yet")
