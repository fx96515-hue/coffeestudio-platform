from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.models.cooperative import Cooperative
from app.schemas.cooperative import CooperativeCreate, CooperativeOut, CooperativeUpdate
from app.services.scoring import recompute_and_persist_cooperative
from app.core.export import DataExporter

router = APIRouter()


@router.get("/", response_model=list[CooperativeOut])
def list_coops(
    db: Session = Depends(get_db), _=Depends(require_role("admin", "analyst", "viewer"))
):
    return db.query(Cooperative).order_by(Cooperative.name.asc()).all()


@router.post("/", response_model=CooperativeOut)
def create_coop(
    payload: CooperativeCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst")),
):
    coop = Cooperative(**payload.model_dump())
    db.add(coop)
    db.commit()
    db.refresh(coop)
    return coop


@router.get("/{coop_id}", response_model=CooperativeOut)
def get_coop(
    coop_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst", "viewer")),
):
    coop = db.query(Cooperative).filter(Cooperative.id == coop_id).first()
    if not coop:
        raise HTTPException(status_code=404, detail="Not found")
    return coop


@router.patch("/{coop_id}", response_model=CooperativeOut)
def update_coop(
    coop_id: int,
    payload: CooperativeUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst")),
):
    coop = db.query(Cooperative).filter(Cooperative.id == coop_id).first()
    if not coop:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(coop, k, v)
    db.commit()
    db.refresh(coop)
    return coop


@router.delete("/{coop_id}")
def delete_coop(
    coop_id: int, db: Session = Depends(get_db), _=Depends(require_role("admin"))
):
    coop = db.query(Cooperative).filter(Cooperative.id == coop_id).first()
    if not coop:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(coop)
    db.commit()
    return {"status": "deleted"}


@router.post("/{coop_id}/recompute_score")
def recompute_score(
    coop_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst")),
):
    coop = db.query(Cooperative).filter(Cooperative.id == coop_id).first()
    if not coop:
        raise HTTPException(status_code=404, detail="Not found")
    breakdown = recompute_and_persist_cooperative(db, coop)
    return {"status": "ok", "coop_id": coop_id, "breakdown": breakdown.__dict__}


@router.get("/export/csv", response_class=StreamingResponse)
def export_cooperatives_csv(
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst", "viewer")),
):
    """Export all cooperatives to CSV format."""
    cooperatives = db.query(Cooperative).order_by(Cooperative.name.asc()).all()
    return DataExporter.cooperatives_to_csv(cooperatives)
