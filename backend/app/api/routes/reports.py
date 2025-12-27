from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.models.report import Report
from app.schemas.report import ReportOut

router = APIRouter()


@router.get("/", response_model=list[ReportOut])
def list_reports(
    limit: int = 30,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst", "viewer")),
):
    return (
        db.query(Report).order_by(Report.report_at.desc()).limit(min(limit, 200)).all()
    )


@router.get("/{report_id}", response_model=ReportOut)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst", "viewer")),
):
    r = db.query(Report).filter(Report.id == report_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    return r
