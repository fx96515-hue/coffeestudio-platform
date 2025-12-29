"""Peru Region Intelligence Service for sourcing analysis."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.region import Region
from app.services.data_sources.peru_data_sources import (
    fetch_jnc_data,
    fetch_minagri_data,
    fetch_senamhi_weather,
)


@dataclass
class RegionIntelligence:
    """Region intelligence data structure."""
    
    id: int
    name: str
    country: str
    elevation_range: Optional[dict]
    climate_data: Optional[dict]
    soil_type: Optional[str]
    growing_conditions_score: Optional[float]
    production_data: Optional[dict]
    economic_data: Optional[dict]
    quality_profile: Optional[dict]
    infrastructure_data: Optional[dict]
    harvest_season: Optional[str]
    cooperatives_count: Optional[int]
    certifications_pct: Optional[dict]
    risk_factors: Optional[dict]
    last_updated: datetime


class PeruRegionIntelService:
    """Service for Peru region intelligence operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_region_intelligence(self, region_name: str) -> Optional[RegionIntelligence]:
        """Get comprehensive intelligence for a specific region.
        
        Args:
            region_name: Name of the region
            
        Returns:
            RegionIntelligence object or None if not found
        """
        stmt = select(Region).where(Region.name == region_name)
        region = self.db.scalar(stmt)
        
        if not region:
            return None
            
        return RegionIntelligence(
            id=region.id,
            name=region.name,
            country=region.country,
            elevation_range=region.elevation_range,
            climate_data=region.climate_data,
            soil_type=region.soil_type,
            growing_conditions_score=region.growing_conditions_score,
            production_data=region.production_data,
            economic_data=region.economic_data,
            quality_profile=region.quality_profile,
            infrastructure_data=region.infrastructure_data,
            harvest_season=region.harvest_season,
            cooperatives_count=region.cooperatives_count,
            certifications_pct=region.certifications_pct,
            risk_factors=region.risk_factors,
            last_updated=region.last_updated,
        )

    def calculate_growing_conditions_score(
        self, 
        climate: Optional[dict],
        elevation: Optional[dict],
        soil: Optional[str]
    ) -> float:
        """Calculate a growing conditions score based on environmental factors.
        
        Scoring:
        - Elevation (30 points): Ideal 1200-2000 masl
        - Climate (40 points): Temperature 15-25°C, rainfall 1200-2000mm
        - Soil (30 points): Based on soil type quality
        
        Args:
            climate: Climate data including temperature and rainfall
            elevation: Elevation range with min, max, avg
            soil: Soil type description
            
        Returns:
            Score from 0-100
        """
        score = 0.0
        
        # Elevation scoring (30 points max)
        if elevation and isinstance(elevation, dict):
            avg_elev = elevation.get("avg")
            if avg_elev:
                if 1200 <= avg_elev <= 2000:
                    score += 30.0
                elif 1000 <= avg_elev < 1200 or 2000 < avg_elev <= 2200:
                    score += 25.0
                elif 800 <= avg_elev < 1000 or 2200 < avg_elev <= 2400:
                    score += 20.0
                else:
                    score += 10.0
        
        # Climate scoring (40 points max)
        if climate and isinstance(climate, dict):
            temp = climate.get("temperature_avg_c")
            rainfall = climate.get("rainfall_mm_annual")
            
            # Temperature component (20 points)
            if temp:
                if 15 <= temp <= 25:
                    score += 20.0
                elif 12 <= temp < 15 or 25 < temp <= 28:
                    score += 15.0
                else:
                    score += 8.0
            
            # Rainfall component (20 points)
            if rainfall:
                if 1200 <= rainfall <= 2000:
                    score += 20.0
                elif 1000 <= rainfall < 1200 or 2000 < rainfall <= 2500:
                    score += 15.0
                else:
                    score += 8.0
        
        # Soil scoring (30 points max)
        if soil:
            soil_lower = soil.lower()
            if any(term in soil_lower for term in ["volcanic", "rich", "fertile"]):
                score += 30.0
            elif any(term in soil_lower for term in ["loam", "clay", "well-drained"]):
                score += 25.0
            else:
                score += 15.0
        
        return min(100.0, score)

    def get_all_regions(self) -> List[Region]:
        """Get all regions in the database.
        
        Returns:
            List of Region objects
        """
        return list(self.db.query(Region).order_by(Region.name).all())

    def refresh_region_data(self, region_name: str) -> Optional[Region]:
        """Refresh region data from external sources.
        
        Args:
            region_name: Name of the region to refresh
            
        Returns:
            Updated Region object or None if not found
        """
        stmt = select(Region).where(Region.name == region_name)
        region = self.db.scalar(stmt)
        
        if not region:
            return None
        
        # Fetch data from external sources
        jnc_data = fetch_jnc_data()
        minagri_data = fetch_minagri_data()
        weather_data = fetch_senamhi_weather()
        
        # Update production data from JNC
        if jnc_data.get("status") == "mock" and region_name in jnc_data.get("data", {}).get("regions", {}):
            region_jnc = jnc_data["data"]["regions"][region_name]
            if not region.production_data:
                region.production_data = {}
            region.production_data.update({
                "production_pct": region_jnc.get("production_pct"),
                "quality_score": region_jnc.get("quality_score"),
            })
        
        # Update climate data from SENAMHI
        if weather_data.get("status") == "mock" and region_name in weather_data.get("data", {}).get("regions", {}):
            region_weather = weather_data["data"]["regions"][region_name]
            region.climate_data = region_weather
        
        # Recalculate growing conditions score
        region.growing_conditions_score = self.calculate_growing_conditions_score(
            region.climate_data,
            region.elevation_range,
            region.soil_type
        )
        
        region.last_updated = datetime.now(timezone.utc)
        
        self.db.add(region)
        self.db.commit()
        self.db.refresh(region)
        
        return region
