from pydantic import BaseModel, Field
from typing import Optional, List


class TrackingEvent(BaseModel):
    timestamp: str
    location: str
    event: str
    details: Optional[str] = None


class ShipmentCreate(BaseModel):
    lot_id: Optional[int] = None
    cooperative_id: Optional[int] = None
    roaster_id: Optional[int] = None
    container_number: str = Field(..., min_length=5, max_length=50)
    bill_of_lading: str
    weight_kg: float = Field(..., gt=0)
    container_type: str = Field(..., pattern="^(20ft|40ft|40ft_hc)$")
    origin_port: str
    destination_port: str
    departure_date: Optional[str] = None
    estimated_arrival: Optional[str] = None
    notes: Optional[str] = None


class ShipmentUpdate(BaseModel):
    current_location: Optional[str] = None
    status: Optional[str] = None
    actual_arrival: Optional[str] = None
    delay_hours: Optional[int] = None
    notes: Optional[str] = None


class TrackingEventCreate(BaseModel):
    timestamp: str
    location: str
    event: str
    details: Optional[str] = None


class ShipmentOut(BaseModel):
    id: int
    lot_id: Optional[int]
    cooperative_id: Optional[int]
    roaster_id: Optional[int]
    container_number: str
    bill_of_lading: str
    weight_kg: float
    container_type: str
    origin_port: str
    destination_port: str
    current_location: Optional[str]
    departure_date: Optional[str]
    estimated_arrival: Optional[str]
    actual_arrival: Optional[str]
    status: str
    status_updated_at: Optional[str]
    delay_hours: int
    tracking_events: Optional[List[TrackingEvent]] = None
    notes: Optional[str]

    class Config:
        from_attributes = True
