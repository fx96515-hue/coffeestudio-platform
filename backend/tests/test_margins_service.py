"""Tests for margins service module."""
import pytest
from datetime import datetime, timezone

from app.services.margins import calc_margin
from app.schemas.margin import MarginCalcRequest


def test_calc_margin_basic():
    """Test basic margin calculation."""
    req = MarginCalcRequest(
        purchase_price_per_kg=5.0,
        landed_costs_per_kg=1.0,
        yield_factor=0.84,
        roast_and_pack_costs_per_kg=2.0,
        selling_price_per_kg=10.0,
        purchase_currency="USD",
        selling_currency="USD"
    )
    
    inputs, outputs = calc_margin(req)
    
    # Verify inputs are preserved
    assert inputs['purchase_price_per_kg'] == 5.0
    assert inputs['landed_costs_per_kg'] == 1.0
    
    # Verify calculations
    assert outputs['green_total_cost_per_kg'] == 6.0  # 5 + 1
    assert outputs['cost_per_kg_roasted_from_green'] == pytest.approx(6.0 / 0.84)
    assert outputs['total_cost_per_kg_roasted'] == pytest.approx(6.0 / 0.84 + 2.0)
    assert outputs['gross_margin_per_kg'] == pytest.approx(10.0 - (6.0 / 0.84 + 2.0))
    assert 'computed_at' in outputs


def test_calc_margin_with_forex():
    """Test margin calculation with forex conversion."""
    req = MarginCalcRequest(
        purchase_price_per_kg=5.0,
        landed_costs_per_kg=1.0,
        yield_factor=0.84,
        roast_and_pack_costs_per_kg=2.0,
        selling_price_per_kg=10.0,
        purchase_currency="USD",
        selling_currency="EUR",
        fx_usd_to_eur=0.85
    )
    
    inputs, outputs = calc_margin(req)
    
    # Verify EUR conversions are present
    assert 'green_total_cost_per_kg_eur' in outputs
    assert 'total_cost_per_kg_roasted_eur' in outputs
    assert outputs['green_total_cost_per_kg_eur'] == pytest.approx(6.0 * 0.85)


def test_calc_margin_negative_margin():
    """Test margin calculation resulting in loss."""
    req = MarginCalcRequest(
        purchase_price_per_kg=8.0,
        landed_costs_per_kg=3.0,
        yield_factor=0.84,
        roast_and_pack_costs_per_kg=3.0,
        selling_price_per_kg=10.0,
        purchase_currency="USD",
        selling_currency="USD"
    )
    
    inputs, outputs = calc_margin(req)
    
    # Total cost per kg roasted = (8+3)/0.84 + 3 = 16.095
    # Selling = 10
    # Margin should be negative
    assert outputs['gross_margin_per_kg'] < 0
    assert outputs['gross_margin_pct'] < 0


def test_calc_margin_zero_selling_price():
    """Test margin calculation with zero selling price."""
    req = MarginCalcRequest(
        purchase_price_per_kg=5.0,
        landed_costs_per_kg=1.0,
        yield_factor=0.84,
        roast_and_pack_costs_per_kg=2.0,
        selling_price_per_kg=0.0,
        purchase_currency="USD",
        selling_currency="USD"
    )
    
    inputs, outputs = calc_margin(req)
    
    # When selling price is 0, margin_pct should be None
    assert outputs['gross_margin_pct'] is None


def test_calc_margin_invalid_yield_factor_zero():
    """Test error when yield factor is zero."""
    req = MarginCalcRequest(
        purchase_price_per_kg=5.0,
        landed_costs_per_kg=1.0,
        yield_factor=0.0,
        roast_and_pack_costs_per_kg=2.0,
        selling_price_per_kg=10.0,
        purchase_currency="USD",
        selling_currency="USD"
    )
    
    with pytest.raises(ValueError, match="yield_factor must be within"):
        calc_margin(req)


def test_calc_margin_invalid_yield_factor_negative():
    """Test error when yield factor is negative."""
    req = MarginCalcRequest(
        purchase_price_per_kg=5.0,
        landed_costs_per_kg=1.0,
        yield_factor=-0.5,
        roast_and_pack_costs_per_kg=2.0,
        selling_price_per_kg=10.0,
        purchase_currency="USD",
        selling_currency="USD"
    )
    
    with pytest.raises(ValueError, match="yield_factor must be within"):
        calc_margin(req)


def test_calc_margin_invalid_yield_factor_over_one():
    """Test error when yield factor is over 1."""
    req = MarginCalcRequest(
        purchase_price_per_kg=5.0,
        landed_costs_per_kg=1.0,
        yield_factor=1.5,
        roast_and_pack_costs_per_kg=2.0,
        selling_price_per_kg=10.0,
        purchase_currency="USD",
        selling_currency="USD"
    )
    
    with pytest.raises(ValueError, match="yield_factor must be within"):
        calc_margin(req)


def test_calc_margin_yield_factor_exactly_one():
    """Test margin calculation with yield factor exactly 1."""
    req = MarginCalcRequest(
        purchase_price_per_kg=5.0,
        landed_costs_per_kg=1.0,
        yield_factor=1.0,
        roast_and_pack_costs_per_kg=2.0,
        selling_price_per_kg=10.0,
        purchase_currency="USD",
        selling_currency="USD"
    )
    
    inputs, outputs = calc_margin(req)
    
    # With yield factor 1, no conversion needed
    assert outputs['cost_per_kg_roasted_from_green'] == 6.0


def test_calc_margin_high_yield_factor():
    """Test margin calculation with high yield factor."""
    req = MarginCalcRequest(
        purchase_price_per_kg=5.0,
        landed_costs_per_kg=1.0,
        yield_factor=0.9,
        roast_and_pack_costs_per_kg=2.0,
        selling_price_per_kg=10.0,
        purchase_currency="USD",
        selling_currency="USD"
    )
    
    inputs, outputs = calc_margin(req)
    
    # Higher yield factor means lower cost per kg roasted
    assert outputs['cost_per_kg_roasted_from_green'] == pytest.approx(6.0 / 0.9)


def test_calc_margin_no_forex_without_proper_currencies():
    """Test that forex is not applied without proper currency setup."""
    req = MarginCalcRequest(
        purchase_price_per_kg=5.0,
        landed_costs_per_kg=1.0,
        yield_factor=0.84,
        roast_and_pack_costs_per_kg=2.0,
        selling_price_per_kg=10.0,
        purchase_currency="USD",
        selling_currency="USD",  # Same currency
        fx_usd_to_eur=0.85
    )
    
    inputs, outputs = calc_margin(req)
    
    # Should not include EUR fields when both currencies are USD
    assert 'green_total_cost_per_kg_eur' not in outputs


def test_calc_margin_no_forex_without_fx_rate():
    """Test that forex is not applied without fx rate."""
    req = MarginCalcRequest(
        purchase_price_per_kg=5.0,
        landed_costs_per_kg=1.0,
        yield_factor=0.84,
        roast_and_pack_costs_per_kg=2.0,
        selling_price_per_kg=10.0,
        purchase_currency="USD",
        selling_currency="EUR",
        fx_usd_to_eur=None
    )
    
    inputs, outputs = calc_margin(req)
    
    # Should not include EUR fields without fx_usd_to_eur
    assert 'green_total_cost_per_kg_eur' not in outputs


def test_calc_margin_timestamp_format():
    """Test that computed_at timestamp is in ISO format."""
    req = MarginCalcRequest(
        purchase_price_per_kg=5.0,
        landed_costs_per_kg=1.0,
        yield_factor=0.84,
        roast_and_pack_costs_per_kg=2.0,
        selling_price_per_kg=10.0,
        purchase_currency="USD",
        selling_currency="USD"
    )
    
    inputs, outputs = calc_margin(req)
    
    # Verify timestamp is valid ISO format
    assert 'computed_at' in outputs
    timestamp = outputs['computed_at']
    # Should be parseable as datetime
    parsed = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    assert isinstance(parsed, datetime)


def test_calc_margin_zero_costs():
    """Test margin calculation with zero costs."""
    req = MarginCalcRequest(
        purchase_price_per_kg=0.0,
        landed_costs_per_kg=0.0,
        yield_factor=0.84,
        roast_and_pack_costs_per_kg=0.0,
        selling_price_per_kg=10.0,
        purchase_currency="USD",
        selling_currency="USD"
    )
    
    inputs, outputs = calc_margin(req)
    
    # All zero costs means 100% margin
    assert outputs['green_total_cost_per_kg'] == 0.0
    assert outputs['gross_margin_per_kg'] == 10.0
    assert outputs['gross_margin_pct'] == 100.0


def test_calc_margin_high_margin():
    """Test margin calculation with high margin scenario."""
    req = MarginCalcRequest(
        purchase_price_per_kg=2.0,
        landed_costs_per_kg=0.5,
        yield_factor=0.84,
        roast_and_pack_costs_per_kg=1.0,
        selling_price_per_kg=20.0,
        purchase_currency="USD",
        selling_currency="USD"
    )
    
    inputs, outputs = calc_margin(req)
    
    # Low costs, high selling price = high margin
    assert outputs['gross_margin_per_kg'] > 10.0
    assert outputs['gross_margin_pct'] > 50.0


def test_calc_margin_precision():
    """Test margin calculation maintains precision."""
    req = MarginCalcRequest(
        purchase_price_per_kg=5.123456,
        landed_costs_per_kg=1.234567,
        yield_factor=0.84,
        roast_and_pack_costs_per_kg=2.345678,
        selling_price_per_kg=10.123456,
        purchase_currency="USD",
        selling_currency="USD"
    )
    
    inputs, outputs = calc_margin(req)
    
    # Verify calculations maintain reasonable precision
    assert outputs['green_total_cost_per_kg'] == pytest.approx(6.358023)
    assert isinstance(outputs['gross_margin_per_kg'], float)
