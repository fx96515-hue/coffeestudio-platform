"""Coffee price prediction ML model."""

import pandas as pd
import numpy as np
from app.ml.base_model import BaseMLModel


class CoffeePriceModel(BaseMLModel):
    """Machine learning model for coffee price prediction."""

    def __init__(self) -> None:
        """Initialize coffee price prediction model."""
        super().__init__(n_estimators=100, max_depth=10, random_state=42)

    def prepare_features(
        self, data: pd.DataFrame
    ) -> tuple[pd.DataFrame, pd.Series | None]:
        """Feature engineering for coffee price prediction.

        Args:
            data: Raw coffee price data

        Returns:
            Tuple of (X features, y target) or (X features, None) for prediction
        """
        df = data.copy()

        # Encode categorical features using base class helper
        categorical_cols = [
            "origin_country",
            "origin_region",
            "variety",
            "process_method",
            "quality_grade",
            "market_source",
        ]
        df = self.encode_categorical(df, categorical_cols)

        # Handle cupping score
        if "cupping_score" in df.columns:
            df["cupping_score"] = df["cupping_score"].fillna(82.0)  # Default score
        else:
            df["cupping_score"] = 82.0

        # Handle ICE C price
        if "ice_c_price_usd_per_lb" in df.columns:
            df["ice_c_price_normalized"] = df["ice_c_price_usd_per_lb"] / 2.0
        else:
            df["ice_c_price_normalized"] = 1.0

        # Certification count from JSON
        if "certifications" in df.columns:
            df["certification_count"] = df["certifications"].apply(
                lambda x: len(x) if isinstance(x, list) else 0
            )
        else:
            df["certification_count"] = 0

        # Extract month/season if date available
        if "date" in df.columns:
            df["month"] = pd.to_datetime(df["date"]).dt.month
        else:
            df["month"] = 1

        # Select features for model
        feature_cols = [
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

        X = df[feature_cols]

        # Return target if available
        y = df["price_usd_per_kg"] if "price_usd_per_kg" in df.columns else None

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

