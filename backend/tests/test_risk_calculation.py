"""Unit tests for risk calculation algorithm."""

import pytest
from app.models.cooperative import Cooperative
from app.services.cooperative_sourcing_analyzer import CooperativeSourcingAnalyzer


def test_risk_calculation_low_risk(db_session):
    """Test risk calculation for low-risk cooperative."""
    coop = Cooperative(
        name="Low Risk Coop",
        quality_score=88.0,
        altitude_m=1500,
        financial_data={
            "annual_revenue_usd": 600000
        },
        export_readiness={
            "export_experience_years": 8,
            "customs_clearance_issues_count": 0
        },
        communication_metrics={
            "avg_email_response_time_hours": 18,
            "missed_meetings_count": 0
        }
    )
    db_session.add(coop)
    db_session.commit()
    
    analyzer = CooperativeSourcingAnalyzer(db_session)
    result = analyzer.calculate_sourcing_risk(coop)
    
    # Should have low total risk
    assert result.risk_score < 30.0
    assert result.financial_risk == 2.0
    assert result.quality_risk == 2.0
    assert result.geographic_risk == 2.0


def test_risk_calculation_high_risk(db_session):
    """Test risk calculation for high-risk cooperative."""
    coop = Cooperative(
        name="High Risk Coop",
        quality_score=55.0,
        altitude_m=2500,
        financial_data={
            "annual_revenue_usd": 50000
        },
        export_readiness={
            "export_experience_years": 1,
            "customs_clearance_issues_count": 5
        },
        communication_metrics={
            "avg_email_response_time_hours": 96,
            "missed_meetings_count": 4
        }
    )
    db_session.add(coop)
    db_session.commit()
    
    analyzer = CooperativeSourcingAnalyzer(db_session)
    result = analyzer.calculate_sourcing_risk(coop)
    
    # Should have high total risk
    assert result.risk_score > 60.0
    assert result.financial_risk == 25.0
    assert result.quality_risk == 20.0
    assert len(result.risk_factors) > 0


def test_risk_calculation_medium_risk(db_session):
    """Test risk calculation for medium-risk cooperative."""
    coop = Cooperative(
        name="Medium Risk Coop",
        quality_score=72.0,
        altitude_m=1200,
        financial_data={
            "annual_revenue_usd": 250000
        },
        export_readiness={
            "export_experience_years": 3,
            "customs_clearance_issues_count": 1
        },
        communication_metrics={
            "avg_email_response_time_hours": 36,
            "missed_meetings_count": 1
        }
    )
    db_session.add(coop)
    db_session.commit()
    
    analyzer = CooperativeSourcingAnalyzer(db_session)
    result = analyzer.calculate_sourcing_risk(coop)
    
    # Should have medium risk
    assert 30.0 < result.risk_score < 60.0
    assert result.financial_risk == 15.0
    assert result.quality_risk == 12.0
