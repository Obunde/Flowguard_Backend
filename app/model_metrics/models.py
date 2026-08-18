"""Model performance tracking: accuracy, confusion matrix, benchmark runs."""
from datetime import datetime

from sqlalchemy import JSON, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base, TenantScopedMixin, UUIDPrimaryKeyMixin


class ModelMetric(Base, UUIDPrimaryKeyMixin, TenantScopedMixin):
    __tablename__ = "model_metric"

    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    dataset_split: Mapped[str | None] = mapped_column(String(20), nullable=True)  # train/val/test

    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[float] = mapped_column(Numeric(10, 6), nullable=False)
    confusion_matrix: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<ModelMetric {self.model_name}@{self.model_version} "
            f"{self.metric_name}={self.metric_value}>"
        )
