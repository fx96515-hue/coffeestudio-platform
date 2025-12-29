"""Unit tests for supply capacity scoring algorithm."""

import pytest
from app.models.cooperative import Cooperative
from app.services.cooperative_sourcing_analyzer import CooperativeSourcingAnalyzer


def test_supply_capacity_high_volume(db_session):
    """Test supply capacity scoring with high volume cooperative."""
    # Create cooperative with high volume
    coop = Cooperative(
        name="High Volume Coop",
        operational_data={
            "farmer_count": 500,
            "storage_capacity_kg": 200000,
            "has_wet_mill": True,
            "has_dry_mill": True
        },
        export_readiness={
            "export_experience_years": 10
        },
        financial_data={
            "export_volume_kg_last_year": 100000
        }
    )
    db_session.add(coop)
    db_session.commit()
    
    analyzer = CooperativeSourcingAnalyzer(db_session)
    result = analyzer.check_supply_capacity(coop)
    
    # Should get high scores for all categories
    assert result.score >= 90.0
    assert result.volume_score == 30.0
    assert result.farmer_count_score == 20.0
    assert result.storage_score == 20.0
    assert result.processing_score == 15.0
    assert result.experience_score == 15.0


def test_supply_capacity_low_volume(db_session):
    """Test supply capacity scoring with low volume cooperative."""
    coop = Cooperative(
        name="Low Volume Coop",
        operational_data={
            "farmer_count": 30,
            "storage_capacity_kg": 10000,
            "has_wet_mill": False,
            "has_dry_mill": False
        },
        export_readiness={
            "export_experience_years": 0
        },
        financial_data={
            "export_volume_kg_last_year": 5000
        }
    )
    db_session.add(coop)
    db_session.commit()
    
    analyzer = CooperativeSourcingAnalyzer(db_session)
    result = analyzer.check_supply_capacity(coop)
    
    # Should get low scores
    assert result.score < 50.0
    assert result.volume_score == 5.0
    assert result.farmer_count_score == 5.0
    assert result.storage_score == 5.0
    assert result.processing_score == 0.0
    assert result.experience_score == 2.0


def test_supply_capacity_medium_volume(db_session):
    """Test supply capacity scoring with medium volume cooperative."""
    coop = Cooperative(
        name="Medium Volume Coop",
        operational_data={
            "farmer_count": 150,
            "storage_capacity_kg": 75000,
            "has_wet_mill": True,
            "has_dry_mill": False
        },
        export_readiness={
            "export_experience_years": 4
        },
        financial_data={
            "export_volume_kg_last_year": 35000
        }
    )
    db_session.add(coop)
    db_session.commit()
    
    analyzer = CooperativeSourcingAnalyzer(db_session)
    result = analyzer.check_supply_capacity(coop)
    
    # Should get medium scores
    assert 50.0 < result.score < 90.0
    assert result.volume_score == 20.0
    assert result.farmer_count_score == 14.0
    assert result.storage_score == 14.0
    assert result.processing_score == 8.0
    assert result.experience_score == 9.0


def test_supply_capacity_empty_data(db_session):
    """Test supply capacity scoring with missing data."""
    coop = Cooperative(name="Empty Data Coop")
    db_session.add(coop)
    db_session.commit()
    
    analyzer = CooperativeSourcingAnalyzer(db_session)
    result = analyzer.check_supply_capacity(coop)
    
    # Should handle missing data gracefully
    assert result.score >= 0.0
    assert result.score <= 100.0
    assert result.volume_score == 5.0  # Minimum score
    assert result.farmer_count_score == 5.0
    assert result.storage_score == 5.0
