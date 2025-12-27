from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.models.cupping import CuppingResult
from app.schemas.cupping import CuppingCreate, CuppingOut


router = APIRouter()


@router.get("/", response_model=list[CuppingOut])
def list_cuppings(limit: int = 200, db: Session = Depends(get_db), _=Depends(require_role("admin", "analyst", "viewer"))):
    return db.query(CuppingResult).order_by(CuppingResult.occurred_at.desc().nullslast()).limit(min(limit, 1000)).all()


@router.post("/", response_model=CuppingOut)
def create(payload: CuppingCreate, db: Session = Depends(get_db), _=Depends(require_role("admin", "analyst"))):
    row = CuppingResult(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row