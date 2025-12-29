"""Unit tests for price benchmarking algorithm."""

import pytest
from app.models.cooperative import Cooperative
from app.models.region import Region
from app.services.cooperative_sourcing_analyzer import CooperativeSourcingAnalyzer


def test_price_benchmark_competitive(db_session):
    """Test price benchmarking with competitive pricing."""
    region = Region(
        name="Test Region",
        economic_data={
            "avg_fob_price": 5.10
        }
    )
    db_session.add(region)
    
    coop = Cooperative(
        name="Competitive Coop",
        region="Test Region",
        quality_score=85.0,
        financial_data={
            "avg_price_achieved_usd_per_kg": 5.05
        }
    )
    db_session.add(coop)
    db_session.commit()
    
    analyzer = CooperativeSourcingAnalyzer(db_session)
    result = analyzer.benchmark_pricing(coop, region, 85.0)
    
    # Should have high score for competitive pricing
    assert result.score > 95.0
    assert result.cooperative_price == 5.05
    assert result.regional_benchmark == 5.10
    assert result.difference_pct < 2.0


def test_price_benchmark_expensive(db_session):
    """Test price benchmarking with expensive pricing."""
    region = Region(
        name="Test Region 2",
        economic_data={
            "avg_fob_price": 5.00
        }
    )
    db_session.add(region)
    
    coop = Cooperative(
        name="Expensive Coop",
        region="Test Region 2",
        quality_score=80.0,
        financial_data={
            "avg_price_achieved_usd_per_kg": 6.00
        }
    )
    db_session.add(coop)
    db_session.commit()
    
    analyzer = CooperativeSourcingAnalyzer(db_session)
    result = analyzer.benchmark_pricing(coop, region, 80.0)
    
    # Should have lower score for expensive pricing
    assert result.score < 70.0
    assert result.cooperative_price == 6.00
    assert result.difference_pct > 15.0


def test_price_benchmark_no_data(db_session):
    """Test price benchmarking with missing data."""
    coop = Cooperative(
        name="No Price Data Coop",
        quality_score=75.0
    )
    db_session.add(coop)
    db_session.commit()
    
    analyzer = CooperativeSourcingAnalyzer(db_session)
    result = analyzer.benchmark_pricing(coop, None, 75.0)
    
    # Should return neutral score with no data
    assert result.score == 50.0
    assert result.cooperative_price is None
    assert result.difference_pct is None


def test_price_benchmark_uses_ico_fallback(db_session):
    """Test that ICO data is used as fallback when no regional data."""
    coop = Cooperative(
        name="ICO Fallback Coop",
        quality_score=82.0,
        financial_data={
            "avg_price_achieved_usd_per_kg": 5.15
        }
    )
    db_session.add(coop)
    db_session.commit()
    
    analyzer = CooperativeSourcingAnalyzer(db_session)
    result = analyzer.benchmark_pricing(coop, None, 82.0)
    
    # Should use ICO fallback (5.10 from mock data)
    assert result.cooperative_price == 5.15
    assert result.regional_benchmark == 5.10  # ICO fallback
    assert result.score > 90.0
