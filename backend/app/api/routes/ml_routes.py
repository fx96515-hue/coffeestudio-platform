"""ML model training and prediction routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import require_role, get_db
from app.schemas.ml import (
    TrainModelOut,
    TrainingStatusOut,
    PurchaseTimingOut,
    PriceForecastOut,
    FeatureImportanceOut,
    ModelComparisonOut,
)
from app.services.ml.training_pipeline import (
    train_freight_model,
    train_price_model,
    compare_models,
)
from app.services.ml.purchase_timing import (
    get_purchase_timing_recommendation,
    get_price_forecast,
)
from app.services.ml.model_management import MLModelManagementService


router = APIRouter()


@router.post("/train/{model_type}", response_model=TrainModelOut)
def train_model(
    model_type: str,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    """Trigger model training.

    model_type: 'freight_cost' or 'coffee_price'
    """
    try:
        if model_type == "freight_cost":
            result = train_freight_model(db)
        elif model_type == "coffee_price":
            result = train_price_model(db)
        else:
            raise HTTPException(
                status_code=400, detail="model_type must be 'freight_cost' or 'coffee_price'"
            )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.get("/training-status", response_model=list[TrainingStatusOut])
async def get_training_status(
    model_type: str | None = None,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst")),
):
    """Get training pipeline status."""
    service = MLModelManagementService(db)
    models = await service.list_models(model_type=model_type)
    return models


@router.get("/optimal-purchase-timing", response_model=PurchaseTimingOut)
def optimal_purchase_timing(
    origin_region: str | None = None,
    target_quantity_kg: float | None = None,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst")),
):
    """Get optimal purchase timing recommendation."""
    result = get_purchase_timing_recommendation(
        db, origin_region=origin_region, target_quantity_kg=target_quantity_kg
    )
    return result


@router.get("/price-forecast", response_model=PriceForecastOut)
def price_forecast(
    origin_region: str | None = None,
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst")),
):
    """Get price forecast for next N days."""
    result = get_price_forecast(db, origin_region=origin_region, days_ahead=days)
    return result


@router.get("/models/{model_id}/feature-importance", response_model=FeatureImportanceOut)
def get_feature_importance(
    model_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst")),
):
    """Get feature importance for a trained XGBoost model."""
    from app.models.ml_model import MLModel
    from app.ml import get_coffee_price_model, get_freight_model
    import os

    # Get model metadata
    ml_model = db.query(MLModel).filter(MLModel.id == model_id).first()
    if not ml_model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Check if model file exists
    if not os.path.exists(ml_model.model_file_path):
        raise HTTPException(status_code=404, detail="Model file not found")

    # Determine algorithm from performance metrics
    algorithm = ml_model.performance_metrics.get("algorithm", "random_forest")
    
    # Only XGBoost models have feature importance
    if algorithm != "xgboost":
        raise HTTPException(
            status_code=400,
            detail="Feature importance is only available for XGBoost models"
        )

    # Load the model and get feature importance
    try:
        if ml_model.model_type == "coffee_price":
            model = get_coffee_price_model(algorithm)
        elif ml_model.model_type == "freight_cost":
            model = get_freight_model(algorithm)
        else:
            raise HTTPException(status_code=400, detail="Unknown model type")

        model.load(ml_model.model_file_path)
        feature_importance = model.get_feature_importance()

        return FeatureImportanceOut(
            model_id=model_id,
            model_type=ml_model.model_type,
            algorithm=algorithm,
            feature_importance=feature_importance,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feature importance: {str(e)}")


@router.post("/compare-models/{model_type}", response_model=ModelComparisonOut)
def compare_model_types(
    model_type: str,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    """Compare Random Forest vs XGBoost models on the same dataset.
    
    model_type: 'freight_cost' or 'coffee_price'
    """
    try:
        result = compare_models(db, model_type)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")
