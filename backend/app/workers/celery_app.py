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
    for idx, (hh, mm) in enumerate(
        settings.refresh_times_list(settings.MARKET_REFRESH_TIMES), start=1
    ):
        sched[f"market_refresh_{idx:02d}"] = {
            "task": "app.workers.tasks.refresh_market",
            "schedule": crontab(minute=mm, hour=hh),
        }
    for idx, (hh, mm) in enumerate(
        settings.refresh_times_list(settings.NEWS_REFRESH_TIMES), start=1
    ):
        sched[f"news_refresh_{idx:02d}"] = {
            "task": "app.workers.tasks.refresh_news",
            "schedule": crontab(minute=mm, hour=hh),
        }

    # Intelligence refresh (every 6 hours by default)
    intelligence_times = getattr(
        settings, "INTELLIGENCE_REFRESH_TIMES", "06:00,12:00,18:00,00:00"
    )
    for idx, (hh, mm) in enumerate(
        settings.refresh_times_list(intelligence_times), start=1
    ):
        sched[f"intelligence_refresh_{idx:02d}"] = {
            "task": "app.workers.tasks.refresh_intelligence",
            "schedule": crontab(minute=mm, hour=hh),
        }

    # Auto-enrich stale entities (daily at 03:00 by default)
    auto_enrich_time = getattr(settings, "AUTO_ENRICH_TIME", "03:00")
    if auto_enrich_time:
        hh, mm = auto_enrich_time.split(":")
        sched["auto_enrich_stale"] = {
            "task": "app.workers.tasks.auto_enrich_stale",
            "schedule": crontab(minute=int(mm), hour=int(hh)),
        }

    return sched


celery.conf.beat_schedule = _build_schedule()

# Ensure task modules are imported/registered when running Celery via -A app.workers.celery_app.celery
from app.workers import tasks  # noqa: F401, E402
