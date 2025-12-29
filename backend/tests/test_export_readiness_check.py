"""Unit tests for export readiness check algorithm."""

import pytest
from app.models.cooperative import Cooperative
from app.services.cooperative_sourcing_analyzer import CooperativeSourcingAnalyzer


def test_export_readiness_full(db_session):
    """Test export readiness with fully prepared cooperative."""
    coop = Cooperative(
        name="Export Ready Coop",
        certifications="Organic, Fair Trade, Rainforest Alliance",
        export_readiness={
            "export_license_number": "EXPORT-12345",
            "export_license_expiry": "2026-12-31",
            "senasa_registered": True,
            "customs_clearance_issues_count": 0,
            "has_document_coordinator": True,
            "containers_exported_lifetime": 50
        }
    )
    db_session.add(coop)
    db_session.commit()
    
    analyzer = CooperativeSourcingAnalyzer(db_session)
    result = analyzer.check_export_readiness(coop)
    
    # Should get perfect score
    assert result.score == 100.0
    assert result.license_valid is True
    assert result.senasa_registered is True
    assert result.certifications_score == 25.0
    assert result.customs_history_score == 15.0
    assert result.document_coordinator is True


def test_export_readiness_minimal(db_session):
    """Test export readiness with minimal preparation."""
    coop = Cooperative(
        name="Minimal Export Coop",
        certifications="",
        export_readiness={
            "senasa_registered": False,
            "customs_clearance_issues_count": 10,
            "has_document_coordinator": False
        }
    )
    db_session.add(coop)
    db_session.commit()
    
    analyzer = CooperativeSourcingAnalyzer(db_session)
    result = analyzer.check_export_readiness(coop)
    
    # Should get low score
    assert result.score < 30.0
    assert result.license_valid is False
    assert result.senasa_registered is False
    assert result.document_coordinator is False


def test_export_readiness_partial(db_session):
    """Test export readiness with partial preparation."""
    coop = Cooperative(
        name="Partial Export Coop",
        certifications="Organic, Fair Trade",
        export_readiness={
            "export_license_number": "EXPORT-67890",
            "export_license_expiry": "2025-06-30",
            "senasa_registered": True,
            "customs_clearance_issues_count": 2,
            "has_document_coordinator": False
        }
    )
    db_session.add(coop)
    db_session.commit()
    
    analyzer = CooperativeSourcingAnalyzer(db_session)
    result = analyzer.check_export_readiness(coop)
    
    # Should get medium score
    assert 60.0 < result.score < 100.0
    assert result.license_valid is True
    assert result.senasa_registered is True
    assert result.certifications_score == 20.0
    assert result.customs_history_score == 10.0


def test_export_readiness_empty_data(db_session):
    """Test export readiness with no data."""
    coop = Cooperative(name="No Data Coop")
    db_session.add(coop)
    db_session.commit()
    
    analyzer = CooperativeSourcingAnalyzer(db_session)
    result = analyzer.check_export_readiness(coop)
    
    # Should handle missing data
    assert result.score >= 0.0
    assert result.score <= 100.0
    assert result.license_valid is False
    assert result.senasa_registered is False
