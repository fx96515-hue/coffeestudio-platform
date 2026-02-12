"""ML module for predictive models."""

from typing import Union
from app.ml.price_model import CoffeePriceModel, CoffeePriceModelXGB
from app.ml.freight_model import FreightCostModel, FreightCostModelXGB


def get_coffee_price_model(model_type: str = "xgboost") -> Union[CoffeePriceModel, CoffeePriceModelXGB]:
    """Factory function to create coffee price prediction models.

    Args:
        model_type: Type of model to create. Options: "xgboost" or "random_forest"

    Returns:
        Instantiated model object

    Raises:
        ValueError: If model_type is not supported
    """
    if model_type == "xgboost":
        return CoffeePriceModelXGB()
    elif model_type == "random_forest":
        return CoffeePriceModel()
    else:
        raise ValueError(f"Unsupported model_type: {model_type}. Use 'xgboost' or 'random_forest'")


def get_freight_model(model_type: str = "xgboost") -> Union[FreightCostModel, FreightCostModelXGB]:
    """Factory function to create freight cost prediction models.

    Args:
        model_type: Type of model to create. Options: "xgboost" or "random_forest"

    Returns:
        Instantiated model object

    Raises:
        ValueError: If model_type is not supported
    """
    if model_type == "xgboost":
        return FreightCostModelXGB()
    elif model_type == "random_forest":
        return FreightCostModel()
    else:
        raise ValueError(f"Unsupported model_type: {model_type}. Use 'xgboost' or 'random_forest'")

