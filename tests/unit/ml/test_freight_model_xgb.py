"""Unit tests for XGBoost freight cost prediction model."""

import pytest
import pandas as pd
import numpy as np
from backend.app.ml.freight_model import FreightCostModelXGB
from backend.app.ml import get_freight_model


def test_freight_cost_model_xgb_initialization():
    """Test that FreightCostModelXGB initializes correctly."""
    model = FreightCostModelXGB()
    assert model.model is not None
    assert isinstance(model.encoders, dict)
    assert len(model.encoders) == 0


def test_freight_cost_model_xgb_prepare_features():
    """Test feature preparation for freight cost model."""
    model = FreightCostModelXGB()
    
    # Create sample data
    data = pd.DataFrame({
        "route": ["Callao-Hamburg", "Santos-Rotterdam"],
        "container_type": ["40ft", "20ft"],
        "season": ["Q1", "Q2"],
        "carrier": ["Maersk", "MSC"],
        "weight_kg": [18000, 10000],
        "fuel_price_index": [105.0, 110.0],
        "port_congestion_score": [45.0, 60.0],
        "freight_cost_usd": [3500, 2000],
    })
    
    X, y = model.prepare_features(data)
    
    # Check that features and target are returned
    assert X is not None
    assert y is not None
    assert len(X) == 2
    assert len(y) == 2
    
    # Check that features are correctly created
    expected_cols = [
        "route_encoded",
        "container_type_encoded",
        "season_encoded",
        "weight_normalized",
        "fuel_price_index",
        "port_congestion_score",
    ]
    assert list(X.columns) == expected_cols


def test_freight_cost_model_xgb_train_and_predict():
    """Test training and prediction with XGBoost model."""
    model = FreightCostModelXGB()
    
    # Create training data
    data = pd.DataFrame({
        "route": ["Callao-Hamburg"] * 25,
        "container_type": ["40ft"] * 25,
        "season": ["Q1"] * 25,
        "carrier": ["Maersk"] * 25,
        "weight_kg": np.random.uniform(15000, 20000, 25),
        "fuel_price_index": np.random.uniform(100, 120, 25),
        "port_congestion_score": np.random.uniform(40, 70, 25),
        "freight_cost_usd": np.random.uniform(3000, 4000, 25),
    })
    
    X, y = model.prepare_features(data)
    
    # Train the model
    model.train(X, y)
    
    # Make predictions
    predictions = model.predict(X)
    
    assert len(predictions) == len(y)
    assert all(p > 0 for p in predictions)


def test_freight_cost_model_xgb_predict_with_confidence():
    """Test prediction with confidence intervals."""
    model = FreightCostModelXGB()
    
    # Create training data
    data = pd.DataFrame({
        "route": ["Callao-Hamburg"] * 35,
        "container_type": ["40ft"] * 35,
        "season": ["Q1"] * 35,
        "carrier": ["Maersk"] * 35,
        "weight_kg": np.random.uniform(15000, 20000, 35),
        "fuel_price_index": np.random.uniform(100, 120, 35),
        "port_congestion_score": np.random.uniform(40, 70, 35),
        "freight_cost_usd": np.random.uniform(3000, 4000, 35),
    })
    
    X, y = model.prepare_features(data)
    model.train(X, y)
    
    # Make predictions with confidence
    predictions, lower, upper = model.predict_with_confidence(X)
    
    assert len(predictions) == len(y)
    assert len(lower) == len(y)
    assert len(upper) == len(y)
    
    # Check that confidence intervals make sense
    assert all(lower[i] <= predictions[i] <= upper[i] for i in range(len(predictions)))


def test_freight_cost_model_xgb_save_and_load(tmp_path):
    """Test saving and loading the model."""
    model = FreightCostModelXGB()
    
    # Create and train model
    data = pd.DataFrame({
        "route": ["Callao-Hamburg"] * 25,
        "container_type": ["40ft"] * 25,
        "season": ["Q1"] * 25,
        "carrier": ["Maersk"] * 25,
        "weight_kg": [18000] * 25,
        "fuel_price_index": [105.0] * 25,
        "port_congestion_score": [50.0] * 25,
        "freight_cost_usd": [3500] * 25,
    })
    
    X, y = model.prepare_features(data)
    model.train(X, y)
    
    # Save model
    model_path = tmp_path / "test_model.joblib"
    model.save(str(model_path))
    
    # Load model
    new_model = FreightCostModelXGB()
    new_model.load(str(model_path))
    
    # Make predictions with both models
    pred1 = model.predict(X)
    pred2 = new_model.predict(X)
    
    # Predictions should be identical
    np.testing.assert_array_almost_equal(pred1, pred2)


def test_freight_cost_model_xgb_feature_importance():
    """Test getting feature importance from trained model."""
    model = FreightCostModelXGB()
    
    # Create training data
    data = pd.DataFrame({
        "route": ["Callao-Hamburg"] * 30,
        "container_type": ["40ft"] * 30,
        "season": ["Q1"] * 30,
        "carrier": ["Maersk"] * 30,
        "weight_kg": np.random.uniform(15000, 20000, 30),
        "fuel_price_index": np.random.uniform(100, 120, 30),
        "port_congestion_score": np.random.uniform(40, 70, 30),
        "freight_cost_usd": np.random.uniform(3000, 4000, 30),
    })
    
    X, y = model.prepare_features(data)
    model.train(X, y)
    
    # Get feature importance
    importance = model.get_feature_importance()
    
    assert isinstance(importance, dict)
    assert len(importance) == 6  # 6 features
    assert all(isinstance(v, float) for v in importance.values())
    assert all(v >= 0 for v in importance.values())


def test_model_factory_xgboost():
    """Test model factory creates XGBoost model."""
    model = get_freight_model("xgboost")
    assert isinstance(model, FreightCostModelXGB)


def test_model_factory_random_forest():
    """Test model factory creates Random Forest model."""
    from backend.app.ml.freight_model import FreightCostModel
    model = get_freight_model("random_forest")
    assert isinstance(model, FreightCostModel)


def test_model_factory_invalid_type():
    """Test model factory raises error for invalid type."""
    with pytest.raises(ValueError):
        get_freight_model("invalid_model_type")
