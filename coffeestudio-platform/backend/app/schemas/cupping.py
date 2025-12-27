from datetime import datetime

from pydantic import BaseModel


class CuppingCreate(BaseModel):
    occurred_at: datetime | None = None
    taster: str | None = None
    cooperative_id: int | None = None
    lot_id: int | None = None
    roaster_id: int | None = None

    sca_score: float | None = None
    aroma: float | None = None
    flavor: float | None = None
    aftertaste: float | None = None
    acidity: float | None = None
    body: float | None = None
    balance: float | None = None
    sweetness: float | None = None
    uniformity: float | None = None
    clean_cup: float | None = None

    descriptors: str | None = None
    defects: str | None = None
    notes: str | None = None
    meta: dict | None = None


class CuppingOut(CuppingCreate):
    id: int

    class Config:
        from_attributes = True