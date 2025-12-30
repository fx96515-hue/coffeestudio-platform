"""Tests for scoring service module."""
import pytest
from datetime import datetime, timezone

from app.services.scoring import (
    compute_cooperative_score,
    recompute_and_persist_cooperative,
    _clamp,
    _map_sca_to_score,
    _get_latest_observation,
    DEFAULT_WEIGHTS,
)
from app.models.cooperative import Cooperative
from app.models.market import MarketObservation


def test_clamp_within_range():
    """Test clamping value within normal range."""
    assert _clamp(50.0) == 50.0
    assert _clamp(0.0) == 0.0
    assert _clamp(100.0) == 100.0


def test_clamp_below_minimum():
    """Test clamping value below minimum."""
    assert _clamp(-10.0) == 0.0
    assert _clamp(-100.0) == 0.0


def test_clamp_above_maximum():
    """Test clamping value above maximum."""
    assert _clamp(110.0) == 100.0
    assert _clamp(200.0) == 100.0


def test_clamp_custom_range():
    """Test clamping with custom range."""
    assert _clamp(5.0, lo=10.0, hi=20.0) == 10.0
    assert _clamp(15.0, lo=10.0, hi=20.0) == 15.0
    assert _clamp(25.0, lo=10.0, hi=20.0) == 20.0


def test_map_sca_to_score_basic():
    """Test SCA score mapping."""
    # SCA 80 -> 60
    assert _map_sca_to_score(80.0) == 60.0
    # SCA 90 -> 100
    assert _map_sca_to_score(90.0) == 100.0
    # SCA 85 -> 80
    assert _map_sca_to_score(85.0) == 80.0


def test_map_sca_to_score_clamping():
    """Test SCA score mapping with clamping."""
    # Very low SCA (70) -> 60 + (70-80)*4 = 60 - 40 = 20, clamped to 20
    assert _map_sca_to_score(70.0) == 20.0
    # Very high SCA should clamp to 100
    assert _map_sca_to_score(95.0) == 100.0


def test_get_latest_observation_found(db):
    """Test retrieving latest market observation."""
    # Create multiple observations
    obs1 = MarketObservation(
        key="COFFEE_C:USD_LB",
        value=1.5,
        observed_at=datetime(2024, 1, 1, tzinfo=timezone.utc)
    )
    obs2 = MarketObservation(
        key="COFFEE_C:USD_LB",
        value=1.8,
        observed_at=datetime(2024, 1, 2, tzinfo=timezone.utc)
    )
    db.add_all([obs1, obs2])
    db.commit()
    
    result = _get_latest_observation(db, "COFFEE_C:USD_LB")
    
    assert result is not None
    assert result.value == 1.8  # Should get the latest


def test_get_latest_observation_not_found(db):
    """Test retrieving non-existent observation."""
    result = _get_latest_observation(db, "NONEXISTENT_KEY")
    assert result is None


def test_compute_cooperative_score_all_fields_set(db):
    """Test scoring with all score fields explicitly set."""
    coop = Cooperative(
        name="Test Coop",
        quality_score=85.0,
        reliability_score=75.0,
        economics_score=80.0,
        region="Cajamarca"
    )
    db.add(coop)
    db.commit()
    
    score = compute_cooperative_score(db, coop)
    
    assert score.quality == 85.0
    assert score.reliability == 75.0
    assert score.economics == 80.0
    assert score.total is not None
    # Total = 85*0.45 + 75*0.30 + 80*0.25
    expected_total = 85 * DEFAULT_WEIGHTS["quality"] + 75 * DEFAULT_WEIGHTS["reliability"] + 80 * DEFAULT_WEIGHTS["economics"]
    assert score.total == pytest.approx(expected_total)
    assert score.confidence > 0.5  # Should have high confidence


def test_compute_cooperative_score_from_meta_sca(db):
    """Test quality score derived from SCA score in meta."""
    coop = Cooperative(
        name="SCA Coop",
        meta={"sca_score": 85.0}
    )
    db.add(coop)
    db.commit()
    
    score = compute_cooperative_score(db, coop)
    
    assert score.quality is not None
    # SCA 85 should map to score 80
    assert score.quality == 80.0
    assert "SCA Score" in " ".join(score.reasons)


def test_compute_cooperative_score_from_meta_reliability(db):
    """Test reliability score from meta."""
    coop = Cooperative(
        name="Reliable Coop",
        meta={"reliability": 90.0}
    )
    db.add(coop)
    db.commit()
    
    score = compute_cooperative_score(db, coop)
    
    assert score.reliability == 90.0


def test_compute_cooperative_score_economics_with_fob_and_market(db):
    """Test economics score calculation using FOB and market reference."""
    # Create market observation
    obs = MarketObservation(
        key="COFFEE_C:USD_LB",
        value=1.0,  # USD per lb
        observed_at=datetime.now(timezone.utc)
    )
    db.add(obs)
    db.commit()
    
    # FOB higher than market = worse economics
    # 1 USD/lb = ~2.2 USD/kg, FOB 4.0 is higher, so economics will be lower
    coop = Cooperative(
        name="Economic Coop",
        meta={"fob_usd_per_kg": 4.0}
    )
    db.add(coop)
    db.commit()
    
    score = compute_cooperative_score(db, coop)
    
    assert score.economics is not None
    # Should calculate economics score based on FOB vs reference
    assert score.economics >= 0


def test_compute_cooperative_score_economics_without_market_ref(db):
    """Test economics score defaults to neutral without market reference."""
    coop = Cooperative(
        name="No Market Ref",
        meta={"fob_usd_per_kg": 5.0}
    )
    db.add(coop)
    db.commit()
    
    score = compute_cooperative_score(db, coop)
    
    assert score.economics == 50.0  # Neutral score


def test_compute_cooperative_score_minimal_data(db):
    """Test scoring with minimal cooperative data."""
    coop = Cooperative(name="Minimal Coop")
    db.add(coop)
    db.commit()
    
    score = compute_cooperative_score(db, coop)
    
    # All scores should be None without data
    assert score.quality is None
    assert score.reliability is None
    assert score.economics is None
    assert score.total is None
    assert score.confidence == 0.0


def test_compute_cooperative_score_confidence_calculation(db):
    """Test confidence calculation based on available signals."""
    # 3 out of 5 signals present
    coop = Cooperative(
        name="Partial Data",
        quality_score=85.0,
        region="Cajamarca",
        contact_email="test@example.com"
    )
    db.add(coop)
    db.commit()
    
    score = compute_cooperative_score(db, coop)
    
    # Signals: quality (1), region (1), contact_email (1) = 3/5
    assert score.confidence == 0.6


def test_compute_cooperative_score_partial_scores(db):
    """Test total score calculation with partial dimension scores."""
    coop = Cooperative(
        name="Partial Scores",
        quality_score=80.0,
        reliability_score=70.0,
        # No economics score
        region="Cusco"
    )
    db.add(coop)
    db.commit()
    
    score = compute_cooperative_score(db, coop)
    
    assert score.quality == 80.0
    assert score.reliability == 70.0
    assert score.economics is None
    # Total should be calculated from available dimensions
    assert score.total is not None
    assert score.total > 0


def test_compute_cooperative_score_clamping():
    """Test that extreme values are clamped to 0-100 range."""
    # This would be tested internally via _clamp
    assert _clamp(150.0) == 100.0
    assert _clamp(-50.0) == 0.0


def test_recompute_and_persist_cooperative(db):
    """Test recomputing and persisting cooperative scores."""
    coop = Cooperative(
        name="Persist Test",
        quality_score=85.0,
        reliability_score=75.0,
        economics_score=80.0,
        region="Puno"
    )
    db.add(coop)
    db.commit()
    initial_id = coop.id
    
    breakdown = recompute_and_persist_cooperative(db, coop)
    
    # Verify breakdown matches
    assert breakdown.quality == 85.0
    assert breakdown.reliability == 75.0
    assert breakdown.economics == 80.0
    
    # Verify persistence
    db.refresh(coop)
    assert coop.quality_score == breakdown.quality
    assert coop.reliability_score == breakdown.reliability
    assert coop.economics_score == breakdown.economics
    assert coop.total_score == breakdown.total
    assert coop.confidence == breakdown.confidence
    assert coop.last_scored_at is not None


def test_recompute_updates_timestamp(db):
    """Test that recompute updates last_scored_at timestamp."""
    coop = Cooperative(
        name="Timestamp Test",
        quality_score=80.0
    )
    db.add(coop)
    db.commit()
    
    before = datetime.now(timezone.utc)
    recompute_and_persist_cooperative(db, coop)
    
    db.refresh(coop)
    assert coop.last_scored_at is not None
    # Handle both naive and aware datetimes
    if coop.last_scored_at.tzinfo is None:
        # Convert before to naive for comparison
        assert coop.last_scored_at >= before.replace(tzinfo=None)
    else:
        assert coop.last_scored_at >= before


def test_compute_cooperative_score_with_altitude(db):
    """Test that altitude contributes to confidence."""
    coop = Cooperative(
        name="High Altitude",
        altitude_m=1800.0,
        quality_score=85.0
    )
    db.add(coop)
    db.commit()
    
    score = compute_cooperative_score(db, coop)
    
    # Should have higher confidence with altitude data
    assert score.confidence >= 0.4


def test_compute_cooperative_score_with_website(db):
    """Test that website contributes to confidence."""
    coop = Cooperative(
        name="With Website",
        website="https://example.com",
        quality_score=85.0
    )
    db.add(coop)
    db.commit()
    
    score = compute_cooperative_score(db, coop)
    
    assert score.confidence >= 0.4


def test_compute_cooperative_score_all_signals(db):
    """Test scoring with all confidence signals present."""
    coop = Cooperative(
        name="All Signals",
        quality_score=85.0,
        reliability_score=75.0,
        economics_score=80.0,
        contact_email="test@example.com",
        region="Cajamarca",
        altitude_m=1800.0
    )
    db.add(coop)
    db.commit()
    
    score = compute_cooperative_score(db, coop)
    
    # All 5 signals present = 100% confidence
    assert score.confidence == 1.0


def test_compute_cooperative_score_reasons_populated(db):
    """Test that reasons list is populated."""
    coop = Cooperative(
        name="Reasons Test",
        quality_score=85.0,
        reliability_score=75.0
    )
    db.add(coop)
    db.commit()
    
    score = compute_cooperative_score(db, coop)
    
    assert len(score.reasons) >= 2
    assert any("Qualität" in r for r in score.reasons)
    assert any("Zuverlässigkeit" in r for r in score.reasons)


def test_default_weights_sum_to_one():
    """Test that default weights sum to 1.0."""
    total_weight = sum(DEFAULT_WEIGHTS.values())
    assert total_weight == pytest.approx(1.0)
