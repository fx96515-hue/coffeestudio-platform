"""Unit tests for XGBoost coffee price prediction model."""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.ml.price_model import CoffeePriceModelXGB, CoffeePriceModel
from app.ml import get_coffee_price_model


def test_coffee_price_model_xgb_initialization():
    """Test that CoffeePriceModelXGB initializes correctly."""
    model = CoffeePriceModelXGB()
    assert model.model is not None
    assert isinstance(model.encoders, dict)
    assert len(model.encoders) == 0


def test_coffee_price_model_xgb_prepare_features():
    """Test feature preparation for coffee price model."""
    model = CoffeePriceModelXGB()
    
    # Create sample data
    data = pd.DataFrame({
        "origin_country": ["Peru", "Colombia"],
        "origin_region": ["Cajamarca", "Huila"],
        "variety": ["Caturra", "Typica"],
        "process_method": ["washed", "natural"],
        "quality_grade": ["specialty", "specialty"],
        "market_source": ["direct", "export"],
        "cupping_score": [85.0, 87.0],
        "certifications": [["organic", "fairtrade"], ["organic"]],
        "ice_c_price_usd_per_lb": [1.5, 1.6],
        "date": ["2024-01-15", "2024-02-20"],
        "price_usd_per_kg": [5.0, 5.5],
    })
    
    X, y = model.prepare_features(data)
    
    # Check that features and target are returned
    assert X is not None
    assert y is not None
    assert len(X) == 2
    assert len(y) == 2
    
    # Check that features are correctly created
    expected_cols = [
        "origin_country_encoded",
        "origin_region_encoded",
        "variety_encoded",
        "process_method_encoded",
        "quality_grade_encoded",
        "cupping_score",
        "certification_count",
        "ice_c_price_normalized",
        "month",
    ]
    assert list(X.columns) == expected_cols


def test_coffee_price_model_xgb_train_and_predict():
    """Test training and prediction with XGBoost model."""
    model = CoffeePriceModelXGB()
    
    # Create training data
    data = pd.DataFrame({
        "origin_country": ["Peru"] * 20,
        "origin_region": ["Cajamarca"] * 20,
        "variety": ["Caturra"] * 20,
        "process_method": ["washed"] * 20,
        "quality_grade": ["specialty"] * 20,
        "market_source": ["direct"] * 20,
        "cupping_score": np.random.uniform(82, 88, 20),
        "certifications": [["organic"]] * 20,
        "ice_c_price_usd_per_lb": np.random.uniform(1.4, 1.8, 20),
        "date": ["2024-01-01"] * 20,
        "price_usd_per_kg": np.random.uniform(4.5, 6.0, 20),
    })
    
    X, y = model.prepare_features(data)
    
    # Train the model
    model.train(X, y)
    
    # Make predictions
    predictions = model.predict(X)
    
    assert len(predictions) == len(y)
    assert all(p > 0 for p in predictions)


def test_coffee_price_model_xgb_predict_with_confidence():
    """Test prediction with confidence intervals."""
    model = CoffeePriceModelXGB()
    
    # Create training data
    data = pd.DataFrame({
        "origin_country": ["Peru"] * 30,
        "origin_region": ["Cajamarca"] * 30,
        "variety": ["Caturra"] * 30,
        "process_method": ["washed"] * 30,
        "quality_grade": ["specialty"] * 30,
        "market_source": ["direct"] * 30,
        "cupping_score": np.random.uniform(82, 88, 30),
        "certifications": [["organic"]] * 30,
        "ice_c_price_usd_per_lb": np.random.uniform(1.4, 1.8, 30),
        "date": ["2024-01-01"] * 30,
        "price_usd_per_kg": np.random.uniform(4.5, 6.0, 30),
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


def test_coffee_price_model_xgb_save_and_load(tmp_path):
    """Test saving and loading the model."""
    model = CoffeePriceModelXGB()
    
    # Create and train model
    data = pd.DataFrame({
        "origin_country": ["Peru"] * 20,
        "origin_region": ["Cajamarca"] * 20,
        "variety": ["Caturra"] * 20,
        "process_method": ["washed"] * 20,
        "quality_grade": ["specialty"] * 20,
        "market_source": ["direct"] * 20,
        "cupping_score": [85.0] * 20,
        "certifications": [["organic"]] * 20,
        "ice_c_price_usd_per_lb": [1.5] * 20,
        "date": ["2024-01-01"] * 20,
        "price_usd_per_kg": [5.0] * 20,
    })
    
    X, y = model.prepare_features(data)
    model.train(X, y)
    
    # Save model
    model_path = tmp_path / "test_model.joblib"
    model.save(str(model_path))
    
    # Load model
    new_model = CoffeePriceModelXGB()
    new_model.load(str(model_path))
    
    # Make predictions with both models
    pred1 = model.predict(X)
    pred2 = new_model.predict(X)
    
    # Predictions should be identical
    np.testing.assert_array_almost_equal(pred1, pred2)


def test_coffee_price_model_xgb_feature_importance():
    """Test getting feature importance from trained model."""
    model = CoffeePriceModelXGB()
    
    # Create training data
    data = pd.DataFrame({
        "origin_country": ["Peru"] * 30,
        "origin_region": ["Cajamarca"] * 30,
        "variety": ["Caturra"] * 30,
        "process_method": ["washed"] * 30,
        "quality_grade": ["specialty"] * 30,
        "market_source": ["direct"] * 30,
        "cupping_score": np.random.uniform(82, 88, 30),
        "certifications": [["organic"]] * 30,
        "ice_c_price_usd_per_lb": np.random.uniform(1.4, 1.8, 30),
        "date": ["2024-01-01"] * 30,
        "price_usd_per_kg": np.random.uniform(4.5, 6.0, 30),
    })
    
    X, y = model.prepare_features(data)
    model.train(X, y)
    
    # Get feature importance
    importance = model.get_feature_importance()
    
    assert isinstance(importance, dict)
    assert len(importance) == 9  # 9 features
    assert all(isinstance(v, float) for v in importance.values())
    assert all(v >= 0 for v in importance.values())


def test_model_factory_xgboost():
    """Test model factory creates XGBoost model."""
    model = get_coffee_price_model("xgboost")
    assert isinstance(model, CoffeePriceModelXGB)


def test_model_factory_random_forest():
    """Test model factory creates Random Forest model."""
    model = get_coffee_price_model("random_forest")
    assert isinstance(model, CoffeePriceModel)


def test_model_factory_invalid_type():
    """Test model factory raises error for invalid type."""
    with pytest.raises(ValueError):
        get_coffee_price_model("invalid_model_type")
