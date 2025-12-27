from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RoasterCreate(BaseModel):
    name: str
    city: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    peru_focus: bool = False
    specialty_focus: bool = True
    price_position: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = "active"
    next_action: Optional[str] = None
    requested_data: Optional[str] = None
    meta: Optional[dict] = None


class RoasterUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    peru_focus: Optional[bool] = None
    specialty_focus: Optional[bool] = None
    price_position: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    next_action: Optional[str] = None
    requested_data: Optional[str] = None
    last_verified_at: Optional[datetime] = None
    total_score: Optional[float] = None
    confidence: Optional[float] = None
    meta: Optional[dict] = None


class RoasterOut(BaseModel):
    id: int
    name: str
    city: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    peru_focus: bool
    specialty_focus: bool
    price_position: Optional[str] = None
    notes: Optional[str] = None

    status: str
    next_action: Optional[str] = None
    requested_data: Optional[str] = None
    last_verified_at: Optional[datetime] = None
    total_score: Optional[float] = None
    confidence: Optional[float] = None
    last_scored_at: Optional[datetime] = None
    meta: Optional[dict] = None

    class Config:
        from_attributes = True
