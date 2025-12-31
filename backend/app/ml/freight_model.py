"""Freight cost prediction ML model."""

import pandas as pd
import numpy as np
from app.ml.base_model import BaseMLModel


class FreightCostModel(BaseMLModel):
    """Machine learning model for freight cost prediction."""

    def __init__(self) -> None:
        """Initialize freight cost prediction model."""
        super().__init__(n_estimators=100, max_depth=10, random_state=42)

    def prepare_features(
        self, data: pd.DataFrame
    ) -> tuple[pd.DataFrame, pd.Series | None]:
        """Feature engineering for freight prediction.

        Args:
            data: Raw freight data with columns like route, container_type, etc.

        Returns:
            Tuple of (X features, y target) or (X features, None) for prediction
        """
        df = data.copy()

        # Encode categorical features using base class helper
        categorical_cols = ["route", "container_type", "season", "carrier"]
        df = self.encode_categorical(df, categorical_cols)

        # Normalize weight
        if "weight_kg" in df.columns:
            df["weight_normalized"] = df["weight_kg"] / 20000.0  # Normalize by max

        # Handle missing optional features
        if "fuel_price_index" in df.columns:
            df["fuel_price_index"] = df["fuel_price_index"].fillna(100.0)
        else:
            df["fuel_price_index"] = 100.0

        if "port_congestion_score" in df.columns:
            df["port_congestion_score"] = df["port_congestion_score"].fillna(50.0)
        else:
            df["port_congestion_score"] = 50.0

        # Select features for model
        feature_cols = [
            "route_encoded",
            "container_type_encoded",
            "season_encoded",
            "weight_normalized",
            "fuel_price_index",
            "port_congestion_score",
        ]

        X = df[feature_cols]

        # Return target if available (training)
        y = df["freight_cost_usd"] if "freight_cost_usd" in df.columns else None

        return X, y

    def predict_with_bounds(
        self, X: pd.DataFrame
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Make predictions with confidence intervals (alias for compatibility).

        Note: This method provides confidence bounds. For confidence score,
        use the base class predict_with_confidence method.

        Args:
            X: Feature dataframe

        Returns:
            Tuple of (predictions, lower_bound, upper_bound)
        """
        predictions = self.predict(X)

        # Use standard deviation from trees for confidence bounds
        tree_predictions = np.array(
            [tree.predict(X) for tree in self.model.estimators_]
        )
        std = np.std(tree_predictions, axis=0)

        lower_bound = predictions - 1.96 * std
        upper_bound = predictions + 1.96 * std

        return predictions, lower_bound, upper_bound
