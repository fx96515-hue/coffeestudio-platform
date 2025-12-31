"""
Data source stubs for Peru coffee data integration.

These are placeholder functions for future integration with external data sources.
Currently return mock/empty data structures to allow the system to function.
"""

from typing import Any


def fetch_jnc_data(region_name: str) -> dict[str, Any]:
    """
    Fetch data from Junta Nacional del Café (Peru's National Coffee Board).

    Stub function - returns empty data structure.
    Future: Will fetch production volumes, quality reports, and market data.

    Args:
        region_name: Name of the coffee region

    Returns:
        Dictionary with JNC data (currently empty)
    """
    return {
        "source": "JNC",
        "available": False,
        "data": {},
        "note": "Integration pending",
    }


def fetch_minagri_data(region_name: str) -> dict[str, Any]:
    """
    Fetch data from Ministerio de Agricultura y Riego (Peru's Ministry of Agriculture).

    Stub function - returns empty data structure.
    Future: Will fetch agricultural statistics, certifications, and support programs.

    Args:
        region_name: Name of the coffee region

    Returns:
        Dictionary with MINAGRI data (currently empty)
    """
    return {
        "source": "MINAGRI",
        "available": False,
        "data": {},
        "note": "Integration pending",
    }


def fetch_senamhi_weather(region_name: str) -> dict[str, Any]:
    """
    Fetch weather data from SENAMHI (Peru's National Meteorological Service).

    Stub function - returns empty data structure.
    Future: Will fetch current weather, forecasts, and historical climate data.

    Args:
        region_name: Name of the coffee region

    Returns:
        Dictionary with SENAMHI weather data (currently empty)
    """
    return {
        "source": "SENAMHI",
        "available": False,
        "data": {},
        "note": "Integration pending",
    }


def fetch_ico_price_data() -> dict[str, Any]:
    """
    Fetch price data from International Coffee Organization (ICO).

    Stub function - returns fallback price data.
    Future: Will fetch live ICO indicator prices and market reports.

    Returns:
        Dictionary with ICO price data (fallback values)
    """
    return {
        "source": "ICO",
        "available": False,
        "fallback_prices": {
            "arabica_mild": {
                "price_usd_per_lb": 2.10,
                "note": "Static fallback - ICO integration pending",
            },
            "peru_fob_benchmark": {
                "price_usd_per_kg": 4.85,
                "note": "Estimated from regional averages",
            },
        },
        "data": {},
        "note": "Using fallback prices - ICO integration pending",
    }
