"""External data sources for Peru sourcing intelligence.

These are placeholder/stub functions for future integration with external APIs.
"""

from typing import Any, Dict


def fetch_jnc_data() -> Dict[str, Any]:
    """Fetch data from Junta Nacional del Café (Peru's National Coffee Board).
    
    TODO: Implement API integration with JNC data sources.
    
    Returns:
        Mock data for development purposes.
    """
    return {
        "status": "mock",
        "data": {
            "total_production_2024_kg": 250000000,
            "export_volume_2024_kg": 200000000,
            "avg_price_usd_per_kg": 5.20,
            "regions": {
                "Cajamarca": {"production_pct": 0.30, "quality_score": 85},
                "Junín": {"production_pct": 0.20, "quality_score": 83},
                "San Martín": {"production_pct": 0.18, "quality_score": 80},
                "Cusco": {"production_pct": 0.15, "quality_score": 87},
                "Amazonas": {"production_pct": 0.08, "quality_score": 86},
                "Puno": {"production_pct": 0.05, "quality_score": 88},
            }
        }
    }


def fetch_minagri_data() -> Dict[str, Any]:
    """Fetch data from Peruvian Ministry of Agriculture.
    
    TODO: Implement API integration with MINAGRI data sources.
    
    Returns:
        Mock data for development purposes.
    """
    return {
        "status": "mock",
        "data": {
            "harvest_forecast_2025": {
                "total_area_hectares": 425000,
                "expected_yield_kg_per_ha": 800,
                "regions": {
                    "Cajamarca": {"area_ha": 127500, "farmers": 45000},
                    "Junín": {"area_ha": 85000, "farmers": 30000},
                    "San Martín": {"area_ha": 76500, "farmers": 28000},
                }
            }
        }
    }


def fetch_senamhi_weather() -> Dict[str, Any]:
    """Fetch weather data from SENAMHI (Peru's National Weather Service).
    
    TODO: Implement API integration with SENAMHI weather data.
    
    Returns:
        Mock data for development purposes.
    """
    return {
        "status": "mock",
        "data": {
            "regions": {
                "Cajamarca": {
                    "temperature_avg_c": 18.5,
                    "rainfall_mm_annual": 1200,
                    "humidity_pct": 75
                },
                "Junín": {
                    "temperature_avg_c": 20.0,
                    "rainfall_mm_annual": 1500,
                    "humidity_pct": 80
                },
                "San Martín": {
                    "temperature_avg_c": 24.0,
                    "rainfall_mm_annual": 2000,
                    "humidity_pct": 85
                }
            }
        }
    }


def fetch_ico_price_data() -> Dict[str, Any]:
    """Fetch coffee price data from International Coffee Organization.
    
    TODO: Implement API integration with ICO price data.
    
    Returns:
        Mock data for development purposes.
    """
    return {
        "status": "mock",
        "data": {
            "arabica_price_usd_per_lb": 2.35,
            "robusta_price_usd_per_lb": 1.05,
            "peru_fob_avg_usd_per_kg": 5.10,
            "trend": "stable",
            "last_updated": "2025-12-29"
        }
    }
