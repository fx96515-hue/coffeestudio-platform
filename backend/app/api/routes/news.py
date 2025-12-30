from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.models.news_item import NewsItem
from app.schemas.news import NewsItemOut, NewsRefreshResponse
from app.services.news import refresh_news


router = APIRouter()


@router.get("/", response_model=list[NewsItemOut])
def list_news(
    topic: str = "peru coffee",
    limit: int = 100,
    days: int = 7,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst", "viewer")),
):
    cutoff = datetime.now(timezone.utc) - timedelta(days=max(0, min(days, 365)))
    q = db.query(NewsItem).filter(NewsItem.topic == topic)
    q = q.filter((NewsItem.retrieved_at.is_(None)) | (NewsItem.retrieved_at >= cutoff))
    return (
        q.order_by(NewsItem.retrieved_at.desc().nullslast())
        .limit(min(limit, 500))
        .all()
    )


@router.post("/refresh", response_model=NewsRefreshResponse)
def refresh(
    topic: str = "peru coffee",
    country: str = "PE",
    max_items: int = 25,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst")),
):
    return refresh_news(db, topic=topic, country=country, max_items=max_items)
