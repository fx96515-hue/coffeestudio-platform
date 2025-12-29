"""API routes for Peru sourcing intelligence."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.models.region import Region
from app.schemas.peru_sourcing import (
    RegionIntelligenceResponse,
    RegionBasicResponse,
    SourcingAnalysisResponse,
    AnalyzeCooperativeRequest,
    RefreshRegionRequest,
)
from app.services.peru_sourcing_intel import PeruRegionIntelService
from app.services.cooperative_sourcing_analyzer import CooperativeSourcingAnalyzer
from app.services.seed_peru_regions import seed_peru_regions


router = APIRouter()


@router.get("/regions", response_model=List[RegionBasicResponse])
def list_regions(
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst", "viewer"))
):
    """List all Peru regions with basic information."""
    service = PeruRegionIntelService(db)
    regions = service.get_all_regions()
    return regions


@router.get("/regions/{name}/intelligence", response_model=RegionIntelligenceResponse)
def get_region_intelligence(
    name: str,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst", "viewer"))
):
    """Get comprehensive intelligence for a specific region."""
    service = PeruRegionIntelService(db)
    intelligence = service.get_region_intelligence(name)
    
    if not intelligence:
        raise HTTPException(status_code=404, detail=f"Region '{name}' not found")
    
    return intelligence


@router.get("/cooperatives/{coop_id}/sourcing-analysis", response_model=SourcingAnalysisResponse)
def get_cooperative_sourcing_analysis(
    coop_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst", "viewer"))
):
    """Get sourcing analysis for a cooperative (from cached scores if available)."""
    analyzer = CooperativeSourcingAnalyzer(db)
    analysis = analyzer.analyze_for_sourcing(coop_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Cooperative with id {coop_id} not found")
    
    return analysis


@router.post("/cooperatives/{coop_id}/analyze", response_model=SourcingAnalysisResponse)
def analyze_cooperative_for_sourcing(
    coop_id: int,
    request: AnalyzeCooperativeRequest = AnalyzeCooperativeRequest(),
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst"))
):
    """Perform fresh sourcing analysis for a cooperative.
    
    This endpoint always recalculates all scores and updates the cooperative record.
    """
    analyzer = CooperativeSourcingAnalyzer(db)
    analysis = analyzer.analyze_for_sourcing(coop_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Cooperative with id {coop_id} not found")
    
    return analysis


@router.post("/regions/refresh")
def refresh_regions_data(
    request: RefreshRegionRequest = RefreshRegionRequest(),
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst"))
):
    """Refresh region data from external sources.
    
    If region_names is provided, only refresh those regions.
    Otherwise, refresh all regions.
    """
    service = PeruRegionIntelService(db)
    
    if request.region_names:
        refreshed = []
        errors = []
        
        for region_name in request.region_names:
            region = service.refresh_region_data(region_name)
            if region:
                refreshed.append(region_name)
            else:
                errors.append(f"Region '{region_name}' not found")
        
        return {
            "status": "completed",
            "refreshed": refreshed,
            "errors": errors if errors else None
        }
    else:
        # Refresh all regions
        regions = service.get_all_regions()
        refreshed = []
        
        for region in regions:
            updated_region = service.refresh_region_data(region.name)
            if updated_region:
                refreshed.append(region.name)
        
        return {
            "status": "completed",
            "refreshed": refreshed,
            "total": len(refreshed)
        }


@router.post("/regions/seed")
def seed_regions(
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst"))
):
    """Seed Peru regions with comprehensive sourcing intelligence data.
    
    This endpoint creates or updates all major Peru coffee regions with
    production, quality, logistics, and risk data.
    """
    result = seed_peru_regions(db)
    return result
