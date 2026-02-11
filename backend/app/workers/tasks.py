import structlog
from datetime import datetime, timezone

import redis
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.report import Report
from app.models.cooperative import Cooperative
from app.models.roaster import Roaster
from app.services.reports import generate_daily_report
from app.services.discovery import seed_discovery
from app.services.enrichment import enrich_cooperative, enrich_roaster
from app.services.data_pipeline.orchestrator import DataPipelineOrchestrator
from app.services.data_pipeline.freshness import DataFreshnessMonitor
from app.workers.celery_app import celery

log = structlog.get_logger()


def _db() -> Session:
    return SessionLocal()


def _redis() -> redis.Redis:
    """Get Redis connection."""
    return redis.from_url(settings.REDIS_URL)


@celery.task(name="app.workers.tasks.refresh_market")
def refresh_market():
    """Refresh market observations and generate a daily report.

    Enhanced with multi-source fallback and circuit breaker protection.
    """
    db = _db()
    redis_client = _redis()
    try:
        now = datetime.now(timezone.utc)

        # Use orchestrator for market data pipeline
        orchestrator = DataPipelineOrchestrator(db, redis_client)
        pipeline_result = orchestrator.run_market_pipeline()

        log.info(
            "market_refresh",
            status=pipeline_result["status"],
            duration_s=pipeline_result["duration_seconds"],
            errors=pipeline_result["errors"],
        )

        # Generate report
        md, payload = generate_daily_report(db)
        rep = Report(
            kind="daily",
            title=f"Tagesreport {now.date().isoformat()}",
            report_at=now,
            markdown=md,
            payload=payload,
        )
        db.add(rep)
        db.commit()
        db.refresh(rep)

        return {
            "status": pipeline_result["status"],
            "pipeline": pipeline_result,
            "report_id": rep.id,
        }
    finally:
        db.close()
        redis_client.close()


@celery.task(name="app.workers.tasks.refresh_news")
def refresh_news():
    """Refresh Market Radar news and ensure Peru region KB is seeded.

    Note: This task is kept for backward compatibility.
    For full intelligence pipeline, use refresh_intelligence instead.
    """
    db = _db()
    redis_client = _redis()
    try:
        orchestrator = DataPipelineOrchestrator(db, redis_client)
        result = orchestrator.run_intelligence_pipeline()
        log.info("news_refresh", **result)
        return result
    finally:
        db.close()
        redis_client.close()


@celery.task(name="app.workers.tasks.refresh_intelligence")
def refresh_intelligence():
    """Refresh Peru intelligence + enrichment pipeline.

    Includes:
    - Peru weather data (OpenMeteo)
    - News refresh
    - Entity enrichment for stale entities
    """
    db = _db()
    redis_client = _redis()
    try:
        orchestrator = DataPipelineOrchestrator(db, redis_client)
        result = orchestrator.run_intelligence_pipeline()
        log.info("intelligence_refresh", **result)
        return result
    finally:
        db.close()
        redis_client.close()


@celery.task(name="app.workers.tasks.auto_enrich_stale")
def auto_enrich_stale():
    """Auto-enrich entities that haven't been updated in KOOPS_STALE_DAYS.

    Finds the top 10 stalest cooperatives and roasters and enriches them.
    """
    db = _db()
    try:
        monitor = DataFreshnessMonitor(db)

        # Get stale cooperatives
        stale_coops = monitor.get_stale_entities(
            "cooperative", settings.KOOPS_STALE_DAYS
        )
        log.info("auto_enrich_stale_cooperatives", count=len(stale_coops))

        enriched_coops = 0
        for coop_id in stale_coops:
            try:
                coop = db.query(Cooperative).get(coop_id)
                if coop:
                    enrich_cooperative(db, coop)
                    enriched_coops += 1
            except Exception as e:
                log.warning(
                    "auto_enrich_cooperative_failed",
                    coop_id=coop_id,
                    error=str(e),
                )

        # Get stale roasters
        stale_roasters = monitor.get_stale_entities(
            "roaster", settings.ROESTER_STALE_DAYS
        )
        log.info("auto_enrich_stale_roasters", count=len(stale_roasters))

        enriched_roasters = 0
        for roaster_id in stale_roasters:
            try:
                roaster = db.query(Roaster).get(roaster_id)
                if roaster:
                    enrich_roaster(db, roaster)
                    enriched_roasters += 1
            except Exception as e:
                log.warning(
                    "auto_enrich_roaster_failed",
                    roaster_id=roaster_id,
                    error=str(e),
                )

        return {
            "status": "ok",
            "cooperatives_enriched": enriched_coops,
            "roasters_enriched": enriched_roasters,
            "total_enriched": enriched_coops + enriched_roasters,
        }
    finally:
        db.close()


@celery.task(name="app.workers.tasks.seed_discovery")
def seed_discovery_task(
    entity_type: str,
    max_entities: int = 100,
    dry_run: bool = False,
    country_filter: str | None = None,
):
    """Seed cooperatives/roasters via Perplexity discovery.

    Notes:
    - Requires PERPLEXITY_API_KEY.
    - Uses conservative upsert: fill empty fields, store evidence URLs.
    """
    db = _db()
    try:
        if entity_type == "both":
            a = seed_discovery(
                db,
                entity_type="cooperative",
                max_entities=max_entities,
                dry_run=dry_run,
                country_filter=country_filter,
            )
            b = seed_discovery(
                db,
                entity_type="roaster",
                max_entities=max_entities,
                dry_run=dry_run,
                country_filter=country_filter,
            )
            return {"cooperatives": a, "roasters": b}
        return seed_discovery(
            db,
            entity_type=entity_type,
            max_entities=max_entities,
            dry_run=dry_run,
            country_filter=country_filter,
        )
    finally:
        db.close()
