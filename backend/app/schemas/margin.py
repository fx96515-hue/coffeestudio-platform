from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MarginCalcRequest(BaseModel):
    # Core inputs (per kg)
    purchase_price_per_kg: float
    purchase_currency: str = "USD"

    # Additive landed costs per kg (freight, insurance, handling, import etc.)
    landed_costs_per_kg: float = 0.0

    # Roasting / processing costs per kg roasted coffee
    roast_and_pack_costs_per_kg: float = 0.0

    # Yield (e.g., green -> roasted). 0.84 means 16% loss.
    yield_factor: float = 0.84

    # Selling price per kg roasted coffee
    selling_price_per_kg: float = 0.0
    selling_currency: str = "EUR"

    # Optional: FX rate used (USD->EUR) if needed by client; calculation here is currency-agnostic unless you provide fx
    fx_usd_to_eur: Optional[float] = None


class MarginCalcResult(BaseModel):
    computed_at: datetime
    inputs: dict
    outputs: dict


class MarginRunOut(BaseModel):
    id: int
    lot_id: int
    profile: str
    computed_at: datetime
    inputs: dict
    outputs: dict

    class Config:
        from_attributes = True
