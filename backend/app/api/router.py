from fastapi import APIRouter

from app.api.routes import auth, cooperatives, roasters, health, discovery
from app.api.routes import sources, market, reports, lots, margins
from app.api.routes import enrich, dedup, news, logistics, outreach, regions
from app.api.routes import kb, cuppings, ml_predictions, peru_sourcing, shipments

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(
    cooperatives.router, prefix="/cooperatives", tags=["cooperatives"]
)
api_router.include_router(roasters.router, prefix="/roasters", tags=["roasters"])
api_router.include_router(discovery.router, prefix="/discovery", tags=["discovery"])
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
api_router.include_router(market.router, prefix="/market", tags=["market"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(lots.router, prefix="/lots", tags=["lots"])
api_router.include_router(margins.router, prefix="/margins", tags=["margins"])
api_router.include_router(enrich.router, prefix="/enrich", tags=["enrich"])
api_router.include_router(dedup.router, prefix="/dedup", tags=["dedup"])
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(regions.router, prefix="/regions", tags=["regions"])
api_router.include_router(logistics.router, prefix="/logistics", tags=["logistics"])
api_router.include_router(outreach.router, prefix="/outreach", tags=["outreach"])
api_router.include_router(kb.router, prefix="/kb", tags=["kb"])
api_router.include_router(cuppings.router, prefix="/cuppings", tags=["cuppings"])
api_router.include_router(ml_predictions.router, prefix="/ml", tags=["ml"])
api_router.include_router(peru_sourcing.router, prefix="/peru", tags=["peru-sourcing"])
api_router.include_router(shipments.router, prefix="/shipments", tags=["shipments"])
