"""Schemas for Peru sourcing intelligence API."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# Region schemas
class RegionIntelligenceResponse(BaseModel):
    """Response schema for region intelligence."""
    
    id: int
    name: str
    country: str
    elevation_range: Optional[dict] = None
    climate_data: Optional[dict] = None
    soil_type: Optional[str] = None
    growing_conditions_score: Optional[float] = None
    production_data: Optional[dict] = None
    economic_data: Optional[dict] = None
    quality_profile: Optional[dict] = None
    infrastructure_data: Optional[dict] = None
    harvest_season: Optional[str] = None
    cooperatives_count: Optional[int] = None
    certifications_pct: Optional[dict] = None
    risk_factors: Optional[dict] = None
    last_updated: datetime

    class Config:
        from_attributes = True


class RegionBasicResponse(BaseModel):
    """Basic region information."""
    
    id: int
    name: str
    country: str
    harvest_season: Optional[str] = None
    cooperatives_count: Optional[int] = None
    growing_conditions_score: Optional[float] = None

    class Config:
        from_attributes = True


# Supply capacity schemas
class SupplyCapacityResponse(BaseModel):
    """Response schema for supply capacity check."""
    
    score: float = Field(ge=0, le=100)
    volume_score: float = Field(ge=0, le=30)
    farmer_count_score: float = Field(ge=0, le=20)
    storage_score: float = Field(ge=0, le=20)
    processing_score: float = Field(ge=0, le=15)
    experience_score: float = Field(ge=0, le=15)
    details: dict


# Export readiness schemas
class ExportReadinessResponse(BaseModel):
    """Response schema for export readiness check."""
    
    score: float = Field(ge=0, le=100)
    license_valid: bool
    senasa_registered: bool
    certifications_score: float = Field(ge=0, le=25)
    customs_history_score: float = Field(ge=0, le=15)
    document_coordinator: bool
    details: dict


# Price benchmark schemas
class PriceBenchmarkResponse(BaseModel):
    """Response schema for price benchmark."""
    
    cooperative_price: Optional[float] = None
    regional_benchmark: Optional[float] = None
    difference_pct: Optional[float] = None
    score: float = Field(ge=0, le=100)
    details: dict


# Risk assessment schemas
class RiskAssessmentResponse(BaseModel):
    """Response schema for risk assessment."""
    
    risk_score: float = Field(ge=0, le=100, description="Total risk score (lower is better)")
    financial_risk: float = Field(ge=0, le=25)
    quality_risk: float = Field(ge=0, le=20)
    delivery_risk: float = Field(ge=0, le=25)
    geographic_risk: float = Field(ge=0, le=15)
    communication_risk: float = Field(ge=0, le=15)
    risk_factors: List[str]


# Complete sourcing analysis schema
class SourcingAnalysisResponse(BaseModel):
    """Response schema for complete sourcing analysis."""
    
    cooperative_id: int
    cooperative_name: str
    supply_capacity: SupplyCapacityResponse
    export_readiness: ExportReadinessResponse
    communication_score: float = Field(ge=0, le=100)
    price_benchmark: PriceBenchmarkResponse
    risk_assessment: RiskAssessmentResponse
    total_score: float = Field(ge=0, le=100)
    recommendation: str


# Request schemas
class AnalyzeCooperativeRequest(BaseModel):
    """Request schema for cooperative analysis."""
    
    force_refresh: bool = Field(default=False, description="Force recalculation of all scores")


class RefreshRegionRequest(BaseModel):
    """Request schema for region data refresh."""
    
    region_names: Optional[List[str]] = Field(
        default=None,
        description="List of region names to refresh. If None, refresh all regions."
    )
