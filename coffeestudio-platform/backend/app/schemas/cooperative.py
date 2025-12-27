from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CooperativeCreate(BaseModel):
    name: str
    region: Optional[str] = None
    altitude_m: Optional[float] = None
    varieties: Optional[str] = None
    certifications: Optional[str] = None
    contact_email: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = "active"
    next_action: Optional[str] = None
    requested_data: Optional[str] = None
    meta: Optional[dict] = None


class CooperativeUpdate(BaseModel):
    name: Optional[str] = None
    region: Optional[str] = None
    altitude_m: Optional[float] = None
    varieties: Optional[str] = None
    certifications: Optional[str] = None
    contact_email: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    next_action: Optional[str] = None
    requested_data: Optional[str] = None
    last_verified_at: Optional[datetime] = None
    meta: Optional[dict] = None


class CooperativeOut(BaseModel):
    id: int
    name: str
    region: Optional[str] = None
    altitude_m: Optional[float] = None
    varieties: Optional[str] = None
    certifications: Optional[str] = None
    contact_email: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None

    status: str
    next_action: Optional[str] = None
    requested_data: Optional[str] = None
    last_verified_at: Optional[datetime] = None

    quality_score: Optional[float] = None
    reliability_score: Optional[float] = None
    economics_score: Optional[float] = None
    total_score: Optional[float] = None
    confidence: Optional[float] = None
    last_scored_at: Optional[datetime] = None

    meta: Optional[dict] = None

    class Config:
        from_attributes = True
