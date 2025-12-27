from pydantic import BaseModel, Field


class LandedCostRequest(BaseModel):
    weight_kg: float = Field(..., gt=0)
    green_price_usd_per_kg: float = Field(..., ge=0)
    incoterm: str = "FOB"
    freight_usd: float = 0.0
    insurance_pct: float = 0.006
    handling_eur: float = 0.0
    inland_trucking_eur: float = 0.0
    duty_pct: float = 0.0
    vat_pct: float = 0.19


class LandedCostResponse(BaseModel):
    status: str
    inputs: dict
    fx: dict
    breakdown_eur: dict