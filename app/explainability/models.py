"""SHAP-based component attribution for prediction/RUL results."""
import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base, TenantScopedMixin, UUIDPrimaryKeyMixin


class FeatureAttribution(Base, UUIDPrimaryKeyMixin, TenantScopedMixin):
    __tablename__ = "feature_attribution"

    pump_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pump.id", ondelete="CASCADE"), nullable=False, index=True
    )
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    # Component-level attribution, e.g. {"bearing": 0.42, "impeller": 0.31,
    # "seal": 0.27}.
    component_scores: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    # Raw per-feature SHAP values, e.g. {"vibration_mean": 0.12, ...}.
    shap_values: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    top_component: Mapped[str | None] = mapped_column(String(50), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<FeatureAttribution pump_id={self.pump_id} computed_at={self.computed_at}>"
