from pydantic import BaseModel
from typing import Optional


class LotCreate(BaseModel):
    cooperative_id: int
    name: str
    crop_year: Optional[int] = None
    incoterm: Optional[str] = None
    price_per_kg: Optional[float] = None
    currency: Optional[str] = None
    weight_kg: Optional[float] = None
    expected_cupping_score: Optional[float] = None
    varieties: Optional[str] = None
    processing: Optional[str] = None
    availability_window: Optional[str] = None
    notes: Optional[str] = None
    meta: Optional[dict] = None


class LotUpdate(BaseModel):
    name: Optional[str] = None
    crop_year: Optional[int] = None
    incoterm: Optional[str] = None
    price_per_kg: Optional[float] = None
    currency: Optional[str] = None
    weight_kg: Optional[float] = None
    expected_cupping_score: Optional[float] = None
    varieties: Optional[str] = None
    processing: Optional[str] = None
    availability_window: Optional[str] = None
    notes: Optional[str] = None
    meta: Optional[dict] = None


class LotOut(BaseModel):
    id: int
    cooperative_id: int
    name: str
    crop_year: Optional[int] = None
    incoterm: Optional[str] = None
    price_per_kg: Optional[float] = None
    currency: Optional[str] = None
    weight_kg: Optional[float] = None
    expected_cupping_score: Optional[float] = None
    varieties: Optional[str] = None
    processing: Optional[str] = None
    availability_window: Optional[str] = None
    notes: Optional[str] = None
    meta: Optional[dict] = None

    class Config:
        from_attributes = True
