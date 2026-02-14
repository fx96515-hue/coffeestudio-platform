from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from celery.result import AsyncResult

from app.api.deps import require_role
from app.db.session import get_db
from app.models.market import MarketObservation
from app.models.user import User
from app.schemas.market import MarketObservationCreate, MarketObservationOut
from app.workers.celery_app import celery
from app.core.audit import AuditLogger

router = APIRouter()


@router.get("/observations", response_model=list[MarketObservationOut])
def list_observations(
    key: str | None = None,
    limit: int = Query(200, ge=1, le=500),
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst", "viewer")),
):
    q = db.query(MarketObservation)
    if key:
        q = q.filter(MarketObservation.key == key)
    return q.order_by(MarketObservation.observed_at.desc()).limit(limit).all()


@router.post("/observations", response_model=MarketObservationOut)
def create_observation(
    payload: MarketObservationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "analyst")),
):
    obs = MarketObservation(**payload.model_dump())
    db.add(obs)
    db.commit()
    db.refresh(obs)

    # Log creation for audit trail
    AuditLogger.log_create(
        db=db,
        user=user,
        entity_type="market_observation",
        entity_id=obs.id,
        entity_data=payload.model_dump(),
    )

    return obs


@router.get("/latest")
def latest_snapshot(
    db: Session = Depends(get_db), _=Depends(require_role("admin", "analyst", "viewer"))
):
    # return latest per key
    keys = ["FX:USD_EUR", "COFFEE_C:USD_LB", "FREIGHT:USD_PER_40FT"]
    out = {}
    for k in keys:
        obs = (
            db.query(MarketObservation)
            .filter(MarketObservation.key == k)
            .order_by(MarketObservation.observed_at.desc())
            .first()
        )
        out[k] = (
            None
            if not obs
            else {
                "value": obs.value,
                "unit": obs.unit,
                "currency": obs.currency,
                "observed_at": obs.observed_at,
            }
        )
    return out


@router.get("/series")
def series(
    key: str,
    limit: int = Query(365, ge=1, le=500),
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst", "viewer")),
):
    """Return a time series for one key (newest -> oldest)."""
    rows = (
        db.query(MarketObservation)
        .filter(MarketObservation.key == key)
        .order_by(MarketObservation.observed_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "observed_at": r.observed_at,
            "value": r.value,
            "unit": r.unit,
            "currency": r.currency,
        }
        for r in rows
    ]


@router.post("/refresh")
def refresh_market_async(_=Depends(require_role("admin", "analyst"))):
    """Enqueue a market refresh via Celery.

    This mirrors the periodic beat job, but allows manual triggering from the UI.
    """
    res = celery.send_task("app.workers.tasks.refresh_market")
    return {"status": "queued", "task_id": res.id}


@router.get("/tasks/{task_id}")
def market_task_status(
    task_id: str, _=Depends(require_role("admin", "analyst", "viewer"))
):
    r = AsyncResult(task_id, app=celery)
    payload = None
    try:
        payload = r.result if r.ready() else None
    except Exception:
        payload = None
    return {"task_id": task_id, "state": r.state, "ready": r.ready(), "result": payload}
