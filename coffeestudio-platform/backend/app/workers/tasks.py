import structlog
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.market import MarketObservation
from app.models.report import Report
from app.models.cooperative import Cooperative
from app.services.scoring import recompute_and_persist_cooperative
from app.services.reports import generate_daily_report
from app.services.discovery import seed_discovery
from app.services.news import refresh_news as refresh_news_service
from app.services.peru_regions import seed_default_regions
from app.services.market_ingest import upsert_market_observation
from app.providers.ecb_fx import fetch_ecb_fx
from app.providers.stooq import fetch_stooq_last_close
from app.workers.celery_app import celery

log = structlog.get_logger()


def _db() -> Session:
    return SessionLocal()


@celery.task(name="app.workers.tasks.refresh_market")
def refresh_market():
    """Refresh market observations and generate a daily report.

    This is the scheduled refresh hook for FX + coffee prices.
    """
    db = _db()
    try:
        now = datetime.now(timezone.utc)

        ingested = []

        # --- FX: USD->EUR (ECB daily reference rates) ---
        fx = fetch_ecb_fx("USD", "EUR")
        if fx:
            obs = upsert_market_observation(
                db,
                key="FX:USD_EUR",
                value=fx.rate,
                unit=None,
                currency=None,
                observed_at=fx.observed_at,
                source_name="ECB Euro FX Reference Rates",
                source_url=fx.source_url,
                raw_text=fx.raw_text,
                meta={"base": fx.base, "quote": fx.quote},
            )
            ingested.append({"key": obs.key, "observed_at": obs.observed_at.isoformat()})

        # --- Coffee: ICE Arabica (Stooq KC.F close) ---
        kc = fetch_stooq_last_close("kc.f")
        if kc:
            obs = upsert_market_observation(
                db,
                key="COFFEE_C:USD_LB",
                value=kc.close,
                unit="lb",
                currency="USD",
                observed_at=kc.observed_at,
                source_name="Stooq (KC.F Coffee - ICE)",
                source_url=kc.source_url,
                raw_text=kc.raw_text,
                meta={"symbol": kc.symbol},
            )
            ingested.append({"key": obs.key, "observed_at": obs.observed_at.isoformat()})

        log.info("market_refresh", status="ok", ingested=len(ingested))

        # --- Recompute cooperative scores ---
        updated = 0
        for coop in db.query(Cooperative).all():
            recompute_and_persist_cooperative(db, coop)
            updated += 1

        # --- Generate report ---
        md, payload = generate_daily_report(db)
        rep = Report(kind="daily", title=f"Tagesreport {now.date().isoformat()}", report_at=now, markdown=md, payload=payload)
        db.add(rep)
        db.commit()
        db.refresh(rep)

        return {"status": "ok", "ingested": ingested, "coops_scored": updated, "report_id": rep.id}
    finally:
        db.close()


@celery.task(name="app.workers.tasks.refresh_news")
def refresh_news():
    """Refresh Market Radar news and ensure Peru region KB is seeded."""
    db = _db()
    try:
        # Seed regions once (idempotent)
        seed_default_regions(db)
        out = refresh_news_service(db, topic="peru coffee", country="PE", max_items=25)
        log.info("news_refresh", **out)
        return out
    finally:
        db.close()


@celery.task(name="app.workers.tasks.seed_discovery")
def seed_discovery_task(entity_type: str, max_entities: int = 100, dry_run: bool = False, country_filter: str | None = None):
    """Seed cooperatives/roasters via Perplexity discovery.

    Notes:
    - Requires PERPLEXITY_API_KEY.
    - Uses conservative upsert: fill empty fields, store evidence URLs.
    """
    db = _db()
    try:
        if entity_type == "both":
            a = seed_discovery(db, entity_type="cooperative", max_entities=max_entities, dry_run=dry_run, country_filter=country_filter)
            b = seed_discovery(db, entity_type="roaster", max_entities=max_entities, dry_run=dry_run, country_filter=country_filter)
            return {"cooperatives": a, "roasters": b}
        return seed_discovery(db, entity_type=entity_type, max_entities=max_entities, dry_run=dry_run, country_filter=country_filter)
    finally:
        db.close()


 
