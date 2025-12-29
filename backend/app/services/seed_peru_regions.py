"""Seed Peru regions with comprehensive sourcing intelligence data."""

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.region import Region


PERU_REGIONS_DATA = [
    {
        "name": "Cajamarca",
        "country": "Peru",
        "elevation_range": {"min": 1200, "max": 2100, "avg": 1650},
        "climate_data": {
            "temperature_avg_c": 18.5,
            "rainfall_mm_annual": 1200,
            "humidity_pct": 75
        },
        "soil_type": "Volcanic, well-drained",
        "production_data": {
            "production_pct_national": 0.30,
            "annual_volume_kg": 75000000,
            "avg_yield_kg_per_ha": 850,
            "primary_varietals": ["Bourbon", "Caturra", "Typica", "Catimor"]
        },
        "economic_data": {
            "avg_fob_price": 5.30,
            "export_volume_kg": 60000000,
            "price_trend": "stable"
        },
        "quality_profile": {
            "typical_cupping_score": 84,
            "flavor_notes": ["chocolate", "nutty", "caramel", "citrus"],
            "body": "medium-full",
            "acidity": "bright"
        },
        "infrastructure_data": {
            "distance_to_callao_km": 870,
            "road_quality": "fair",
            "trucking_cost_usd_per_kg": 0.12,
            "trucking_time_days": 2
        },
        "harvest_season": "April - September",
        "cooperatives_count": 85,
        "certifications_pct": {
            "organic": 0.45,
            "fairtrade": 0.38,
            "rainforest_alliance": 0.25
        },
        "risk_factors": {
            "weather": "Rainy season can affect road access",
            "quality": "Drying quality varies by cooperative",
            "logistics": "Remote areas require careful planning"
        }
    },
    {
        "name": "Junín",
        "country": "Peru",
        "elevation_range": {"min": 1000, "max": 1800, "avg": 1400},
        "climate_data": {
            "temperature_avg_c": 20.0,
            "rainfall_mm_annual": 1500,
            "humidity_pct": 80
        },
        "soil_type": "Clay loam, fertile",
        "production_data": {
            "production_pct_national": 0.20,
            "annual_volume_kg": 50000000,
            "avg_yield_kg_per_ha": 900,
            "primary_varietals": ["Caturra", "Catuaí", "Typica", "Pache"]
        },
        "economic_data": {
            "avg_fob_price": 5.10,
            "export_volume_kg": 40000000,
            "price_trend": "stable"
        },
        "quality_profile": {
            "typical_cupping_score": 83,
            "flavor_notes": ["fruity", "chocolate", "honey", "floral"],
            "body": "medium",
            "acidity": "medium-bright"
        },
        "infrastructure_data": {
            "distance_to_callao_km": 320,
            "road_quality": "good",
            "trucking_cost_usd_per_kg": 0.08,
            "trucking_time_days": 1
        },
        "harvest_season": "May - September",
        "cooperatives_count": 62,
        "certifications_pct": {
            "organic": 0.50,
            "fairtrade": 0.42,
            "rainforest_alliance": 0.30
        },
        "risk_factors": {
            "weather": "Occasional frost at high elevations",
            "quality": "Processing consistency varies",
            "logistics": "BEST logistics in Peru - close to port"
        }
    },
    {
        "name": "San Martín",
        "country": "Peru",
        "elevation_range": {"min": 800, "max": 1500, "avg": 1150},
        "climate_data": {
            "temperature_avg_c": 24.0,
            "rainfall_mm_annual": 2000,
            "humidity_pct": 85
        },
        "soil_type": "Loamy, high organic matter",
        "production_data": {
            "production_pct_national": 0.18,
            "annual_volume_kg": 45000000,
            "avg_yield_kg_per_ha": 950,
            "primary_varietals": ["Caturra", "Catuaí", "Bourbon", "Catimor"]
        },
        "economic_data": {
            "avg_fob_price": 4.90,
            "export_volume_kg": 36000000,
            "price_trend": "increasing"
        },
        "quality_profile": {
            "typical_cupping_score": 81,
            "flavor_notes": ["chocolate", "nutty", "sweet", "mild"],
            "body": "medium",
            "acidity": "low-medium"
        },
        "infrastructure_data": {
            "distance_to_callao_km": 920,
            "road_quality": "fair",
            "trucking_cost_usd_per_kg": 0.14,
            "trucking_time_days": 3
        },
        "harvest_season": "April - August",
        "cooperatives_count": 78,
        "certifications_pct": {
            "organic": 0.60,
            "fairtrade": 0.35,
            "rainforest_alliance": 0.28
        },
        "risk_factors": {
            "weather": "High humidity - drying challenges",
            "quality": "Lower elevation affects cup quality",
            "logistics": "Longer transport times require planning"
        }
    },
    {
        "name": "Cusco",
        "country": "Peru",
        "elevation_range": {"min": 1500, "max": 2200, "avg": 1850},
        "climate_data": {
            "temperature_avg_c": 17.0,
            "rainfall_mm_annual": 1400,
            "humidity_pct": 70
        },
        "soil_type": "Volcanic, well-drained",
        "production_data": {
            "production_pct_national": 0.15,
            "annual_volume_kg": 37500000,
            "avg_yield_kg_per_ha": 750,
            "primary_varietals": ["Typica", "Bourbon", "Caturra", "Villa Sarchi"]
        },
        "economic_data": {
            "avg_fob_price": 5.60,
            "export_volume_kg": 30000000,
            "price_trend": "increasing"
        },
        "quality_profile": {
            "typical_cupping_score": 86,
            "flavor_notes": ["stone fruit", "floral", "honey", "citrus", "complex"],
            "body": "medium-light",
            "acidity": "bright-vibrant"
        },
        "infrastructure_data": {
            "distance_to_callao_km": 1100,
            "road_quality": "challenging",
            "trucking_cost_usd_per_kg": 0.16,
            "trucking_time_days": 3
        },
        "harvest_season": "May - October",
        "cooperatives_count": 45,
        "certifications_pct": {
            "organic": 0.52,
            "fairtrade": 0.40,
            "rainforest_alliance": 0.35
        },
        "risk_factors": {
            "weather": "Mountain weather can be unpredictable",
            "quality": "Excellent quality potential but requires care",
            "logistics": "Mountain roads can be challenging - plan carefully"
        }
    },
    {
        "name": "Amazonas",
        "country": "Peru",
        "elevation_range": {"min": 1200, "max": 2100, "avg": 1650},
        "climate_data": {
            "temperature_avg_c": 19.0,
            "rainfall_mm_annual": 1600,
            "humidity_pct": 78
        },
        "soil_type": "Rich, well-drained",
        "production_data": {
            "production_pct_national": 0.08,
            "annual_volume_kg": 20000000,
            "avg_yield_kg_per_ha": 800,
            "primary_varietals": ["Caturra", "Bourbon", "Typica", "Catimor"]
        },
        "economic_data": {
            "avg_fob_price": 5.50,
            "export_volume_kg": 16000000,
            "price_trend": "stable"
        },
        "quality_profile": {
            "typical_cupping_score": 85,
            "flavor_notes": ["fruity", "floral", "citrus", "sweet", "clean"],
            "body": "medium",
            "acidity": "bright"
        },
        "infrastructure_data": {
            "distance_to_callao_km": 1200,
            "road_quality": "fair",
            "trucking_cost_usd_per_kg": 0.15,
            "trucking_time_days": 3
        },
        "harvest_season": "April - September",
        "cooperatives_count": 32,
        "certifications_pct": {
            "organic": 0.55,
            "fairtrade": 0.45,
            "rainforest_alliance": 0.32
        },
        "risk_factors": {
            "weather": "Remote location with infrastructure dependencies",
            "quality": "Excellent micro-lot potential",
            "logistics": "Careful cooperative selection important"
        }
    },
    {
        "name": "Puno",
        "country": "Peru",
        "elevation_range": {"min": 1300, "max": 2000, "avg": 1650},
        "climate_data": {
            "temperature_avg_c": 16.5,
            "rainfall_mm_annual": 1100,
            "humidity_pct": 65
        },
        "soil_type": "Well-drained, moderate fertility",
        "production_data": {
            "production_pct_national": 0.05,
            "annual_volume_kg": 12500000,
            "avg_yield_kg_per_ha": 700,
            "primary_varietals": ["Bourbon", "Typica", "Caturra", "Catuaí"]
        },
        "economic_data": {
            "avg_fob_price": 5.70,
            "export_volume_kg": 10000000,
            "price_trend": "stable"
        },
        "quality_profile": {
            "typical_cupping_score": 87,
            "flavor_notes": ["floral", "sweet", "honey", "citrus", "delicate"],
            "body": "light-medium",
            "acidity": "vibrant"
        },
        "infrastructure_data": {
            "distance_to_callao_km": 1400,
            "road_quality": "fair-challenging",
            "trucking_cost_usd_per_kg": 0.18,
            "trucking_time_days": 4
        },
        "harvest_season": "April - August",
        "cooperatives_count": 24,
        "certifications_pct": {
            "organic": 0.48,
            "fairtrade": 0.38,
            "rainforest_alliance": 0.30
        },
        "risk_factors": {
            "weather": "Border region with unique terroir",
            "quality": "Very sweet, floral profiles - high quality",
            "logistics": "Most complex logistics - long inland routes"
        }
    }
]


def seed_peru_regions(db: Session) -> dict:
    """Seed the regions table with Peru coffee regions data.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with seeding results
    """
    created = 0
    updated = 0
    
    for region_data in PERU_REGIONS_DATA:
        stmt = select(Region).where(Region.name == region_data["name"])
        existing_region = db.scalar(stmt)
        
        if not existing_region:
            # Create new region
            from app.services.peru_sourcing_intel import PeruRegionIntelService
            service = PeruRegionIntelService(db)
            
            region = Region(**region_data)
            
            # Calculate growing conditions score
            region.growing_conditions_score = service.calculate_growing_conditions_score(
                region_data.get("climate_data"),
                region_data.get("elevation_range"),
                region_data.get("soil_type")
            )
            
            db.add(region)
            created += 1
        else:
            # Update existing region with new data
            for key, value in region_data.items():
                if key not in ["name", "country"]:  # Don't update primary identifiers
                    setattr(existing_region, key, value)
            
            # Recalculate growing conditions score
            from app.services.peru_sourcing_intel import PeruRegionIntelService
            service = PeruRegionIntelService(db)
            existing_region.growing_conditions_score = service.calculate_growing_conditions_score(
                existing_region.climate_data,
                existing_region.elevation_range,
                existing_region.soil_type
            )
            
            updated += 1
    
    db.commit()
    
    return {
        "status": "success",
        "created": created,
        "updated": updated,
        "total": len(PERU_REGIONS_DATA)
    }
