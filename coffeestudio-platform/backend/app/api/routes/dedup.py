from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.schemas.dedup import DedupPairOut
from app.services.dedup import suggest_duplicates


router = APIRouter()


@router.get("/suggest", response_model=list[DedupPairOut])
def suggest(entity_type: str, threshold: float = 90.0, limit: int = 50, db: Session = Depends(get_db), _=Depends(require_role("admin", "analyst"))):
    try:
        return suggest_duplicates(db, entity_type=entity_type, threshold=threshold, limit_pairs=limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))