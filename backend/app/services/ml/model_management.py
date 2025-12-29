"""ML model management service."""

from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ml_model import MLModel


class MLModelManagementService:
    """Service for managing ML model lifecycle."""

    def __init__(self, db: Session):
        self.db = db

    async def list_models(
        self, model_type: str | None = None
    ) -> list[dict[str, Any]]:
        """List all ML models with metadata.

        Args:
            model_type: Optional filter by model type

        Returns:
            List of model metadata dictionaries
        """
        stmt = select(MLModel)

        if model_type:
            stmt = stmt.where(MLModel.model_type == model_type)

        stmt = stmt.order_by(MLModel.training_date.desc())

        result = self.db.execute(stmt)
        models = result.scalars().all()

        return [
            {
                "id": m.id,
                "model_name": m.model_name,
                "model_type": m.model_type,
                "model_version": m.model_version,
                "training_date": m.training_date.isoformat(),
                "performance_metrics": m.performance_metrics,
                "training_data_count": m.training_data_count,
                "status": m.status,
            }
            for m in models
        ]

    async def get_active_model(self, model_type: str) -> dict[str, Any] | None:
        """Get currently active model for type.

        Args:
            model_type: Type of model to retrieve

        Returns:
            Model metadata dictionary or None
        """
        stmt = (
            select(MLModel)
            .where(MLModel.model_type == model_type)
            .where(MLModel.status == "active")
            .order_by(MLModel.training_date.desc())
            .limit(1)
        )
        result = self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return {
            "id": model.id,
            "model_name": model.model_name,
            "model_type": model.model_type,
            "model_version": model.model_version,
            "training_date": model.training_date.isoformat(),
            "features_used": model.features_used,
            "performance_metrics": model.performance_metrics,
            "training_data_count": model.training_data_count,
            "model_file_path": model.model_file_path,
            "status": model.status,
        }

    async def update_model_status(
        self, model_id: int, new_status: str
    ) -> dict[str, Any]:
        """Update model status.

        Args:
            model_id: ID of model to update
            new_status: New status (training, active, deprecated)

        Returns:
            Updated model metadata
        """
        stmt = select(MLModel).where(MLModel.id == model_id)
        result = self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return {"status": "error", "message": "Model not found"}

        model.status = new_status
        self.db.commit()
        self.db.refresh(model)

        return {
            "status": "success",
            "model_id": model.id,
            "new_status": model.status,
        }

    async def trigger_model_retraining(self, model_type: str) -> dict[str, Any]:
        """Trigger model retraining job.

        This is a placeholder for a background job that would:
        1. Fetch latest historical data
        2. Retrain model
        3. Evaluate performance
        4. If improved, set as active
        5. Deprecate old model

        Args:
            model_type: Type of model to retrain

        Returns:
            Job status dictionary
        """
        # This would typically queue a Celery task
        return {
            "status": "queued",
            "model_type": model_type,
            "message": "Model retraining job queued. This is a placeholder implementation.",
        }

    async def get_model_performance(self, model_id: int) -> dict[str, Any] | None:
        """Get detailed performance metrics for a model.

        Args:
            model_id: ID of model to retrieve

        Returns:
            Performance metrics dictionary or None
        """
        stmt = select(MLModel).where(MLModel.id == model_id)
        result = self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return {
            "model_id": model.id,
            "model_name": model.model_name,
            "model_type": model.model_type,
            "training_date": model.training_date.isoformat(),
            "performance_metrics": model.performance_metrics,
            "training_data_count": model.training_data_count,
            "features_used": model.features_used,
        }
