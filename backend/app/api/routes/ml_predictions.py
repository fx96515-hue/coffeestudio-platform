"""API routes for ML predictions."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.schemas.ml_predictions import (
    FreightPredictionRequest,
    FreightPrediction,
    TransitTimeRequest,
    TransitTimePrediction,
    FreightCostTrend,
    CoffeePricePredictionRequest,
    CoffeePricePrediction,
    PriceForecastRequest,
    PriceForecast,
    OptimalPurchaseTimingRequest,
    OptimalPurchaseTiming,
    MLModelResponse,
    FreightDataImport,
    PriceDataImport,
    DataImportResponse,
)
from app.services.ml.freight_prediction import FreightPredictionService
from app.services.ml.price_prediction import CoffeePricePredictionService
from app.services.ml.model_management import MLModelManagementService
from app.services.ml.data_collection import DataCollectionService

router = APIRouter()


@router.post("/predict-freight", response_model=FreightPrediction)
async def predict_freight_cost(
    request: FreightPredictionRequest,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst", "viewer")),
):
    """Predict freight cost for a shipment."""
    service = FreightPredictionService(db)
    result = await service.predict_freight_cost(
        origin_port=request.origin_port,
        destination_port=request.destination_port,
        weight_kg=request.weight_kg,
        container_type=request.container_type,
        departure_date=request.departure_date,
    )
    return result


@router.post("/predict-transit-time", response_model=TransitTimePrediction)
async def predict_transit_time(
    request: TransitTimeRequest,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst", "viewer")),
):
    """Predict transit time for a route."""
    service = FreightPredictionService(db)
    result = await service.predict_transit_time(
        origin_port=request.origin_port,
        destination_port=request.destination_port,
        departure_date=request.departure_date,
    )
    return result


@router.get("/freight-cost-trend", response_model=FreightCostTrend)
async def get_freight_cost_trend(
    route: str,
    months_back: int = 12,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst", "viewer")),
):
    """Get historical freight cost trend for a route."""
    service = FreightPredictionService(db)
    result = await service.get_cost_trend(route=route, months_back=months_back)
    return result


@router.post("/predict-coffee-price", response_model=CoffeePricePrediction)
async def predict_coffee_price(
    request: CoffeePricePredictionRequest,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst", "viewer")),
):
    """Predict coffee price based on attributes."""
    service = CoffeePricePredictionService(db)
    result = await service.predict_coffee_price(
        origin_country=request.origin_country,
        origin_region=request.origin_region,
        variety=request.variety,
        process_method=request.process_method,
        quality_grade=request.quality_grade,
        cupping_score=request.cupping_score,
        certifications=request.certifications,
        forecast_date=request.forecast_date,
    )
    return result


@router.post("/forecast-price-trend", response_model=PriceForecast)
async def forecast_price_trend(
    request: PriceForecastRequest,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst", "viewer")),
):
    """Forecast price trend for a region."""
    service = CoffeePricePredictionService(db)
    result = await service.forecast_price_trend(
        origin_region=request.origin_region, months_ahead=request.months_ahead
    )
    return result


@router.post("/optimal-purchase-timing", response_model=OptimalPurchaseTiming)
async def calculate_optimal_purchase_timing(
    request: OptimalPurchaseTimingRequest,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst", "viewer")),
):
    """Calculate optimal purchase timing based on price forecasts."""
    service = CoffeePricePredictionService(db)
    result = await service.calculate_optimal_purchase_timing(
        origin_region=request.origin_region,
        target_price_usd_per_kg=request.target_price_usd_per_kg,
    )
    return result


@router.get("/models", response_model=list[MLModelResponse])
async def list_ml_models(
    model_type: str | None = None,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst")),
):
    """List all ML models with optional type filter."""
    service = MLModelManagementService(db)
    models = await service.list_models(model_type=model_type)
    return models


@router.get("/models/{model_id}", response_model=dict)
async def get_model_details(
    model_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst")),
):
    """Get detailed information about a specific model."""
    service = MLModelManagementService(db)
    model = await service.get_model_performance(model_id)

    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    return model


@router.post("/models/{model_id}/retrain", response_model=dict)
async def retrain_model(
    model_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    """Trigger retraining for a specific model."""
    service = MLModelManagementService(db)

    # Get model to find its type
    model = await service.get_model_performance(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    result = await service.trigger_model_retraining(model["model_type"])
    return result


@router.post("/data/import-freight", response_model=DataImportResponse)
async def import_freight_data(
    data: list[FreightDataImport],
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    """Import historical freight data for ML training."""
    service = DataCollectionService(db)

    # Convert Pydantic models to dicts
    data_dicts = [record.model_dump() for record in data]

    try:
        count = await service.import_freight_data(data_dicts)
        return DataImportResponse(
            status="success",
            records_imported=count,
            message=f"Successfully imported {count} freight records",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")


@router.post("/data/import-prices", response_model=DataImportResponse)
async def import_price_data(
    data: list[PriceDataImport],
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    """Import historical coffee price data for ML training."""
    service = DataCollectionService(db)

    # Convert Pydantic models to dicts
    data_dicts = [record.model_dump() for record in data]

    try:
        count = await service.import_price_data(data_dicts)
        return DataImportResponse(
            status="success",
            records_imported=count,
            message=f"Successfully imported {count} price records",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")
