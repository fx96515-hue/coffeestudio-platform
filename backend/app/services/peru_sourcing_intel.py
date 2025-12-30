"""
Peru Region Intelligence Service.

Provides comprehensive intelligence on Peru coffee regions including:
- Growing conditions scoring
- Production data
- Infrastructure assessment
- External data integration
"""

from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.region import Region
from app.services.data_sources.peru_data_sources import (
    fetch_jnc_data,
    fetch_minagri_data,
    fetch_senamhi_weather
)


class PeruRegionIntelService:
    """Service for Peru region intelligence and analysis."""

    def __init__(self, db: Session):
        self.db = db

    def get_region_intelligence(self, region_name: str) -> dict[str, Any] | None:
        """
        Get comprehensive intelligence for a Peru coffee region.
        
        Args:
            region_name: Name of the region (e.g., "Cajamarca", "Junín")
            
        Returns:
            Dictionary with region intelligence or None if not found
        """
        stmt = select(Region).where(Region.name == region_name, Region.country == "Peru")
        region = self.db.scalar(stmt)
        
        if not region:
            return None
            
        # Calculate growing conditions score
        growing_score = self.calculate_growing_conditions_score(region)
        
        return {
            "name": region.name,
            "country": region.country,
            "description": region.description,
            "elevation_range": {
                "min_m": region.elevation_min_m,
                "max_m": region.elevation_max_m
            },
            "climate": {
                "avg_temperature_c": region.avg_temperature_c,
                "rainfall_mm": region.rainfall_mm,
                "humidity_pct": region.humidity_pct
            },
            "soil_type": region.soil_type,
            "production": {
                "volume_kg": region.production_volume_kg,
                "share_pct": region.production_share_pct,
                "harvest_months": region.harvest_months
            },
            "quality": {
                "typical_varieties": region.typical_varieties,
                "typical_processing": region.typical_processing,
                "profile": region.quality_profile,
                "consistency_score": region.quality_consistency_score
            },
            "logistics": {
                "main_port": region.main_port,
                "transport_time_hours": region.transport_time_hours,
                "cost_per_kg": region.logistics_cost_per_kg,
                "infrastructure_score": region.infrastructure_score
            },
            "risks": {
                "weather": region.weather_risk,
                "political": region.political_risk,
                "logistics": region.logistics_risk
            },
            "scores": {
                "growing_conditions": growing_score,
                "infrastructure": region.infrastructure_score or 0,
                "quality_consistency": region.quality_consistency_score or 0
            }
        }

    def calculate_growing_conditions_score(self, region: Region) -> float:
        """
        Calculate growing conditions score (0-100).
        
        Scoring algorithm:
        - Elevation (30 points): Optimal 1200-2000m
        - Climate (40 points): Temperature 18-22°C, Rainfall 1500-2500mm
        - Soil (30 points): Based on soil quality assessment
        
        Args:
            region: Region model instance
            
        Returns:
            Score from 0-100
        """
        score = 0.0
        
        # Elevation score (30 points)
        if region.elevation_min_m and region.elevation_max_m:
            avg_elevation = (region.elevation_min_m + region.elevation_max_m) / 2
            if 1200 <= avg_elevation <= 2000:
                score += 30
            elif 1000 <= avg_elevation < 1200 or 2000 < avg_elevation <= 2200:
                score += 25
            elif 800 <= avg_elevation < 1000 or 2200 < avg_elevation <= 2400:
                score += 20
            else:
                score += 10
        
        # Climate score (40 points)
        climate_points = 0
        
        # Temperature (20 points of climate)
        if region.avg_temperature_c:
            if 18 <= region.avg_temperature_c <= 22:
                climate_points += 20
            elif 16 <= region.avg_temperature_c < 18 or 22 < region.avg_temperature_c <= 24:
                climate_points += 15
            elif 14 <= region.avg_temperature_c < 16 or 24 < region.avg_temperature_c <= 26:
                climate_points += 10
            else:
                climate_points += 5
        
        # Rainfall (20 points of climate)
        if region.rainfall_mm:
            if 1500 <= region.rainfall_mm <= 2500:
                climate_points += 20
            elif 1200 <= region.rainfall_mm < 1500 or 2500 < region.rainfall_mm <= 3000:
                climate_points += 15
            elif 1000 <= region.rainfall_mm < 1200 or 3000 < region.rainfall_mm <= 3500:
                climate_points += 10
            else:
                climate_points += 5
        
        score += climate_points
        
        # Soil score (30 points)
        if region.soil_type:
            soil_lower = region.soil_type.lower()
            if any(term in soil_lower for term in ["volcanic", "loam", "rich"]):
                score += 30
            elif any(term in soil_lower for term in ["clay", "sandy loam"]):
                score += 25
            elif "sandy" in soil_lower:
                score += 15
            else:
                score += 20  # neutral/unknown
        
        return round(score, 2)

    def refresh_region_data(self, region_name: str) -> dict[str, Any]:
        """
        Refresh region data from external sources.
        
        Args:
            region_name: Name of the region
            
        Returns:
            Dictionary with refresh status and data sources
        """
        # Fetch from external sources
        jnc_data = fetch_jnc_data(region_name)
        minagri_data = fetch_minagri_data(region_name)
        weather_data = fetch_senamhi_weather(region_name)
        
        # Currently just return status since sources are stubs
        # Future: Update region model with fresh data
        
        return {
            "region": region_name,
            "refreshed": True,
            "sources": {
                "jnc": jnc_data,
                "minagri": minagri_data,
                "senamhi": weather_data
            },
            "note": "External data sources are stubs - integration pending"
        }
