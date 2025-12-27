from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.models.roaster import Roaster
from app.schemas.roaster import RoasterCreate, RoasterOut, RoasterUpdate

router = APIRouter()


@router.get("/", response_model=list[RoasterOut])
def list_roasters(
    db: Session = Depends(get_db), _=Depends(require_role("admin", "analyst", "viewer"))
):
    return db.query(Roaster).order_by(Roaster.name.asc()).all()


@router.post("/", response_model=RoasterOut)
def create_roaster(
    payload: RoasterCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst")),
):
    r = Roaster(**payload.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.get("/{roaster_id}", response_model=RoasterOut)
def get_roaster(
    roaster_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst", "viewer")),
):
    r = db.query(Roaster).filter(Roaster.id == roaster_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    return r


@router.patch("/{roaster_id}", response_model=RoasterOut)
def update_roaster(
    roaster_id: int,
    payload: RoasterUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst")),
):
    r = db.query(Roaster).filter(Roaster.id == roaster_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/{roaster_id}")
def delete_roaster(
    roaster_id: int, db: Session = Depends(get_db), _=Depends(require_role("admin"))
):
    r = db.query(Roaster).filter(Roaster.id == roaster_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(r)
    db.commit()
    return {"status": "deleted"}
