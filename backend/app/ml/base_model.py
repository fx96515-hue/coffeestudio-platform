"""Base class for ML models to reduce code duplication."""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib


class BaseMLModel(ABC):
    """Base machine learning model with common functionality."""

    def __init__(
        self, n_estimators: int = 100, max_depth: int = 10, random_state: int = 42
    ) -> None:
        """Initialize the ML model.

        Args:
            n_estimators: Number of trees in the random forest
            max_depth: Maximum depth of trees
            random_state: Random seed for reproducibility
        """
        self.model = RandomForestRegressor(
            n_estimators=n_estimators, max_depth=max_depth, random_state=random_state
        )
        self.encoders: dict[str, LabelEncoder] = {}
        self.is_trained = False

    @property
    def feature_names(self) -> list[str]:
        """Get feature names used by the model."""
        if hasattr(self.model, "feature_names_in_"):
            return list(self.model.feature_names_in_)
        return []

    @abstractmethod
    def prepare_features(
        self, data: pd.DataFrame
    ) -> tuple[pd.DataFrame, pd.Series | None]:
        """Feature engineering - must be implemented by subclasses.

        Args:
            data: Raw input data

        Returns:
            Tuple of (X features, y target) or (X features, None) for prediction
        """
        pass

    def train(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """Train the model.

        Args:
            X: Feature matrix
            y: Target vector

        Returns:
            Dictionary with training metrics
        """
        self.model.fit(X, y)
        self.is_trained = True

        train_score = self.model.score(X, y)

        return {
            "train_r2": train_score,
            "n_samples": len(X),
            "n_features": X.shape[1],
            "feature_names": list(X.columns) if hasattr(X, "columns") else [],
        }

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions.

        Args:
            X: Feature matrix

        Returns:
            Array of predictions
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        return self.model.predict(X)

    def predict_with_confidence(self, X: pd.DataFrame) -> tuple[float, float]:
        """Predict with confidence based on tree variance.

        Args:
            X: Single-row feature matrix

        Returns:
            Tuple of (prediction, confidence_score)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        predictions = self.model.predict(X)

        # Get predictions from all trees
        tree_predictions = np.array(
            [tree.predict(X) for tree in self.model.estimators_]
        )

        # Calculate confidence as inverse of coefficient of variation
        mean_pred = np.mean(tree_predictions)
        std_pred = np.std(tree_predictions)

        if mean_pred == 0:
            confidence = 0.5
        else:
            cv = abs(std_pred / mean_pred)  # Coefficient of variation
            confidence = max(0.0, min(1.0, 1.0 - cv))  # Inverse, bounded [0,1]

        return float(predictions[0]), float(confidence)

    def save(self, path: str) -> None:
        """Save model to disk.

        Args:
            path: File path for saving the model
        """
        model_data = {
            "model": self.model,
            "encoders": self.encoders,
            "is_trained": self.is_trained,
        }
        joblib.dump(model_data, path)

    def load(self, path: str) -> None:
        """Load model from disk.

        Args:
            path: File path for loading the model
        """
        model_data = joblib.load(path)
        self.model = model_data["model"]
        self.encoders = model_data["encoders"]
        self.is_trained = model_data.get("is_trained", True)

    def encode_categorical(
        self, df: pd.DataFrame, categorical_cols: list[str]
    ) -> pd.DataFrame:
        """Helper method to encode categorical columns.

        Args:
            df: DataFrame with categorical columns
            categorical_cols: List of column names to encode

        Returns:
            DataFrame with encoded columns added
        """
        for col in categorical_cols:
            if col in df.columns:
                if col not in self.encoders:
                    self.encoders[col] = LabelEncoder()
                    # Fit if training
                    if not df[col].empty:
                        self.encoders[col].fit(df[col].astype(str))
                try:
                    df[f"{col}_encoded"] = self.encoders[col].transform(
                        df[col].astype(str)
                    )
                except ValueError:
                    # Handle unknown labels during prediction
                    df[f"{col}_encoded"] = 0
        return df
