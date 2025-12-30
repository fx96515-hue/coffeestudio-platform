"""Tests for logistics service module."""
import pytest
from datetime import datetime, timezone

from app.services.logistics import calc_landed_cost, _latest_usd_eur, DEFAULT_USD_EUR
from app.models.market import MarketObservation


def test_latest_usd_eur_with_observation(db):
    """Test retrieving latest USD/EUR rate from database."""
    obs = MarketObservation(
        key="FX:USD_EUR",
        value=0.95,
        observed_at=datetime.now(timezone.utc)
    )
    db.add(obs)
    db.commit()
    
    rate, source = _latest_usd_eur(db)
    
    assert rate == 0.95
    assert "obs:" in source


def test_latest_usd_eur_fallback(db):
    """Test fallback to default rate when no observation exists."""
    rate, source = _latest_usd_eur(db)
    
    assert rate == DEFAULT_USD_EUR
    assert source == "fallback"


def test_calc_landed_cost_basic(db):
    """Test basic landed cost calculation."""
    result = calc_landed_cost(
        db,
        weight_kg=1000.0,
        green_price_usd_per_kg=5.0,
        freight_usd=2000.0
    )
    
    assert result['status'] == 'ok'
    assert 'calculated_at' in result
    assert 'inputs' in result
    assert 'fx' in result
    assert 'breakdown_eur' in result
    
    # Verify inputs are stored
    assert result['inputs']['weight_kg'] == 1000.0
    assert result['inputs']['green_price_usd_per_kg'] == 5.0
    
    # Verify breakdown contains expected fields
    breakdown = result['breakdown_eur']
    assert 'goods' in breakdown
    assert 'freight' in breakdown
    assert 'insurance' in breakdown
    assert 'total' in breakdown
    assert 'landed_eur_per_kg' in breakdown


def test_calc_landed_cost_with_fx_rate(db):
    """Test landed cost calculation with custom FX rate."""
    # Set custom FX rate
    obs = MarketObservation(
        key="FX:USD_EUR",
        value=0.90,
        observed_at=datetime.now(timezone.utc)
    )
    db.add(obs)
    db.commit()
    
    result = calc_landed_cost(
        db,
        weight_kg=1000.0,
        green_price_usd_per_kg=5.0,
        freight_usd=1000.0
    )
    
    assert result['fx']['usd_eur'] == 0.90
    # Goods in EUR = 1000 * 5 * 0.90 = 4500
    assert result['breakdown_eur']['goods'] == pytest.approx(4500.0)


def test_calc_landed_cost_with_all_costs(db):
    """Test landed cost with all cost components."""
    result = calc_landed_cost(
        db,
        weight_kg=1000.0,
        green_price_usd_per_kg=5.0,
        freight_usd=2000.0,
        insurance_pct=0.01,
        handling_eur=500.0,
        inland_trucking_eur=300.0,
        duty_pct=0.05,
        vat_pct=0.19
    )
    
    breakdown = result['breakdown_eur']
    assert breakdown['handling'] == 500.0
    assert breakdown['inland_trucking'] == 300.0
    assert breakdown['duty'] > 0
    assert breakdown['vat'] > 0


def test_calc_landed_cost_zero_weight_error(db):
    """Test error when weight is zero."""
    with pytest.raises(ValueError, match="weight_kg must be > 0"):
        calc_landed_cost(
            db,
            weight_kg=0.0,
            green_price_usd_per_kg=5.0
        )


def test_calc_landed_cost_negative_weight_error(db):
    """Test error when weight is negative."""
    with pytest.raises(ValueError, match="weight_kg must be > 0"):
        calc_landed_cost(
            db,
            weight_kg=-100.0,
            green_price_usd_per_kg=5.0
        )


def test_calc_landed_cost_negative_price_error(db):
    """Test error when green price is negative."""
    with pytest.raises(ValueError, match="green_price_usd_per_kg must be >= 0"):
        calc_landed_cost(
            db,
            weight_kg=1000.0,
            green_price_usd_per_kg=-5.0
        )


def test_calc_landed_cost_zero_price(db):
    """Test landed cost with zero green price."""
    result = calc_landed_cost(
        db,
        weight_kg=1000.0,
        green_price_usd_per_kg=0.0,
        freight_usd=1000.0
    )
    
    # Should work with zero price
    assert result['breakdown_eur']['goods'] == 0.0
    assert result['status'] == 'ok'


def test_calc_landed_cost_incoterm_normalization(db):
    """Test that incoterm is normalized."""
    result = calc_landed_cost(
        db,
        weight_kg=1000.0,
        green_price_usd_per_kg=5.0,
        incoterm="fob"
    )
    
    assert result['inputs']['incoterm'] == "FOB"


def test_calc_landed_cost_negative_costs_clamped(db):
    """Test that negative costs are clamped to zero."""
    result = calc_landed_cost(
        db,
        weight_kg=1000.0,
        green_price_usd_per_kg=5.0,
        freight_usd=-500.0,  # Negative
        handling_eur=-200.0,  # Negative
        inland_trucking_eur=-100.0  # Negative
    )
    
    # Negative values should be treated as 0
    breakdown = result['breakdown_eur']
    assert breakdown['freight'] >= 0
    assert breakdown['handling'] == 0
    assert breakdown['inland_trucking'] == 0


def test_calc_landed_cost_insurance_calculation(db):
    """Test insurance cost calculation."""
    obs = MarketObservation(
        key="FX:USD_EUR",
        value=1.0,  # 1:1 for simplicity
        observed_at=datetime.now(timezone.utc)
    )
    db.add(obs)
    db.commit()
    
    result = calc_landed_cost(
        db,
        weight_kg=1000.0,
        green_price_usd_per_kg=5.0,
        freight_usd=1000.0,
        insurance_pct=0.01  # 1%
    )
    
    # Insurance = (goods + freight) * insurance_pct
    # = (5000 + 1000) * 0.01 = 60
    assert result['breakdown_eur']['insurance'] == pytest.approx(60.0)


def test_calc_landed_cost_cif_calculation(db):
    """Test CIF value calculation."""
    obs = MarketObservation(
        key="FX:USD_EUR",
        value=1.0,
        observed_at=datetime.now(timezone.utc)
    )
    db.add(obs)
    db.commit()
    
    result = calc_landed_cost(
        db,
        weight_kg=1000.0,
        green_price_usd_per_kg=5.0,
        freight_usd=1000.0,
        insurance_pct=0.01
    )
    
    # CIF = goods + freight + insurance
    # = 5000 + 1000 + 60 = 6060
    assert result['breakdown_eur']['cif'] == pytest.approx(6060.0)


def test_calc_landed_cost_duty_calculation(db):
    """Test duty calculation."""
    obs = MarketObservation(
        key="FX:USD_EUR",
        value=1.0,
        observed_at=datetime.now(timezone.utc)
    )
    db.add(obs)
    db.commit()
    
    result = calc_landed_cost(
        db,
        weight_kg=1000.0,
        green_price_usd_per_kg=5.0,
        freight_usd=1000.0,
        insurance_pct=0.01,
        duty_pct=0.05  # 5% duty
    )
    
    # Duty = CIF * duty_pct
    cif = result['breakdown_eur']['cif']
    expected_duty = cif * 0.05
    assert result['breakdown_eur']['duty'] == pytest.approx(expected_duty)


def test_calc_landed_cost_vat_calculation(db):
    """Test VAT calculation."""
    obs = MarketObservation(
        key="FX:USD_EUR",
        value=1.0,
        observed_at=datetime.now(timezone.utc)
    )
    db.add(obs)
    db.commit()
    
    result = calc_landed_cost(
        db,
        weight_kg=1000.0,
        green_price_usd_per_kg=5.0,
        freight_usd=1000.0,
        insurance_pct=0.01,
        duty_pct=0.05,
        handling_eur=100.0,
        inland_trucking_eur=50.0,
        vat_pct=0.19
    )
    
    # VAT base = CIF + duty + handling + trucking
    vat_base = result['breakdown_eur']['vat_base']
    expected_vat = vat_base * 0.19
    assert result['breakdown_eur']['vat'] == pytest.approx(expected_vat)


def test_calc_landed_cost_per_kg(db):
    """Test landed cost per kg calculation."""
    result = calc_landed_cost(
        db,
        weight_kg=1000.0,
        green_price_usd_per_kg=5.0,
        freight_usd=1000.0
    )
    
    total = result['breakdown_eur']['total']
    per_kg = result['breakdown_eur']['landed_eur_per_kg']
    
    # Per kg should be total / weight
    assert per_kg == pytest.approx(total / 1000.0)


def test_calc_landed_cost_zero_duty_default(db):
    """Test that duty defaults to zero."""
    result = calc_landed_cost(
        db,
        weight_kg=1000.0,
        green_price_usd_per_kg=5.0
    )
    
    # Default duty should be 0
    assert result['inputs']['duty_pct'] == 0.0
    assert result['breakdown_eur']['duty'] == 0.0


def test_calc_landed_cost_default_vat(db):
    """Test that VAT defaults to 19%."""
    result = calc_landed_cost(
        db,
        weight_kg=1000.0,
        green_price_usd_per_kg=5.0
    )
    
    # Default VAT should be 19%
    assert result['inputs']['vat_pct'] == 0.19


def test_calc_landed_cost_timestamp(db):
    """Test that calculated_at timestamp is present."""
    result = calc_landed_cost(
        db,
        weight_kg=1000.0,
        green_price_usd_per_kg=5.0
    )
    
    assert isinstance(result['calculated_at'], datetime)
