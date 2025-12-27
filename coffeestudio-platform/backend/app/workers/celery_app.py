from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery = Celery(
    "coffeestudio",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery.conf.update(
    timezone=settings.TZ,
    enable_utc=True,
    task_track_started=True,
    task_time_limit=60 * 10,
    broker_connection_retry_on_startup=True,
)

def _build_schedule() -> dict:
    """Build Celery beat schedule from ENV-driven refresh times."""
    sched: dict = {}
    for idx, (hh, mm) in enumerate(settings.refresh_times_list(settings.MARKET_REFRESH_TIMES), start=1):
        sched[f"market_refresh_{idx:02d}"] = {
            "task": "app.workers.tasks.refresh_market",
            "schedule": crontab(minute=mm, hour=hh),
        }
    for idx, (hh, mm) in enumerate(settings.refresh_times_list(settings.NEWS_REFRESH_TIMES), start=1):
        sched[f"news_refresh_{idx:02d}"] = {
            "task": "app.workers.tasks.refresh_news",
            "schedule": crontab(minute=mm, hour=hh),
        }
    return sched


celery.conf.beat_schedule = _build_schedule()
