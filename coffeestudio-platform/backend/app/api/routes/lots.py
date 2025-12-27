from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.models.lot import Lot
from app.schemas.lot import LotCreate, LotOut, LotUpdate

router = APIRouter()


@router.get("/", response_model=list[LotOut])
def list_lots(
    cooperative_id: int | None = None,
    limit: int = 200,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst", "viewer")),
):
    q = db.query(Lot)
    if cooperative_id is not None:
        q = q.filter(Lot.cooperative_id == cooperative_id)
    return q.order_by(Lot.created_at.desc()).limit(min(limit, 1000)).all()


@router.post("/", response_model=LotOut)
def create_lot(payload: LotCreate, db: Session = Depends(get_db), _=Depends(require_role("admin", "analyst"))):
    lot = Lot(**payload.model_dump())
    db.add(lot)
    db.commit()
    db.refresh(lot)
    return lot


@router.get("/{lot_id}", response_model=LotOut)
def get_lot(lot_id: int, db: Session = Depends(get_db), _=Depends(require_role("admin", "analyst", "viewer"))):
    lot = db.query(Lot).filter(Lot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Not found")
    return lot


@router.patch("/{lot_id}", response_model=LotOut)
def update_lot(lot_id: int, payload: LotUpdate, db: Session = Depends(get_db), _=Depends(require_role("admin", "analyst"))):
    lot = db.query(Lot).filter(Lot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(lot, k, v)
    db.commit()
    db.refresh(lot)
    return lot


@router.delete("/{lot_id}")
def delete_lot(lot_id: int, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    lot = db.query(Lot).filter(Lot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(lot)
    db.commit()
    return {"status": "deleted"}
