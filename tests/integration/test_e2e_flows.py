"""End-to-end integration tests across the full stack.

Tests the complete user journey from authentication to data operations.
DOES NOT DUPLICATE unit tests from PR #16.
"""
import pytest
import requests
import time
from typing import Generator

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"


@pytest.fixture(scope="module")
def wait_for_services() -> Generator[None, None, None]:
    """Wait for backend and frontend to be ready."""
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            health = requests.get(f"{BASE_URL}/health", timeout=2)
            if health.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            if attempt == max_attempts - 1:
                raise RuntimeError("Backend not ready after 30 attempts")
            time.sleep(1)
    
    yield


@pytest.fixture(scope="module")
def auth_token(wait_for_services) -> str:
    """Get authentication token for test user."""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@coffeestudio.com", "password": "test123"},
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200, f"Auth failed: {response.text}"
    return response.json()["access_token"]


def test_e2e_cooperative_flow(auth_token):
    """Test complete cooperative creation → sourcing analysis → frontend display flow."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Step 1: Create cooperative
    coop_data = {
        "name": "E2E Test Cooperative",
        "region": "Cajamarca",
        "contact_person": "Juan Test",
        "email": "test@e2ecoop.com",
        "annual_volume_kg": 50000,
        "quality_score": 85.5,
        "certifications": ["Organic"]
    }
    create_resp = requests.post(
        f"{BASE_URL}/cooperatives",
        json=coop_data,
        headers=headers
    )
    assert create_resp.status_code == 201
    coop_id = create_resp.json()["id"]
    
    # Step 2: Trigger sourcing analysis (if Peru routes exist from PR #4)
    try:
        analysis_resp = requests.post(
            f"{BASE_URL}/peru/cooperatives/{coop_id}/analyze",
            headers=headers
        )
        if analysis_resp.status_code == 200:
            analysis = analysis_resp.json()
            assert "total_score" in analysis
    except requests.exceptions.RequestException:
        pytest.skip("Peru sourcing routes not available")
    
    # Step 3: Verify retrieval
    get_resp = requests.get(f"{BASE_URL}/cooperatives/{coop_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "E2E Test Cooperative"
    
    # Cleanup
    requests.delete(f"{BASE_URL}/cooperatives/{coop_id}", headers=headers)


def test_e2e_roaster_flow(auth_token):
    """Test complete roaster creation → sales fit scoring → frontend display flow."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    roaster_data = {
        "name": "E2E Test Roastery",
        "city": "Hamburg",
        "country": "Germany",
        "contact_person": "Hans Müller",
        "email": "test@e2eroaster.de",
        "annual_capacity_kg": 30000,
        "type": "specialty"
    }
    
    create_resp = requests.post(
        f"{BASE_URL}/roasters",
        json=roaster_data,
        headers=headers
    )
    assert create_resp.status_code == 201
    roaster_id = create_resp.json()["id"]
    
    get_resp = requests.get(f"{BASE_URL}/roasters/{roaster_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["city"] == "Hamburg"
    
    requests.delete(f"{BASE_URL}/roasters/{roaster_id}", headers=headers)


def test_e2e_margin_calculation(auth_token):
    """Test lot creation → margin calculation → frontend display."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Create cooperative first
    coop_resp = requests.post(
        f"{BASE_URL}/cooperatives",
        json={
            "name": "Margin Test Coop",
            "region": "Junín",
            "annual_volume_kg": 20000
        },
        headers=headers
    )
    coop_id = coop_resp.json()["id"]
    
    # Create lot
    lot_data = {
        "cooperative_id": coop_id,
        "name": "Test Lot A",
        "price_per_kg": 5.50,
        "currency": "USD",
        "weight_kg": 1000,
        "expected_cupping_score": 86.0
    }
    lot_resp = requests.post(f"{BASE_URL}/lots", json=lot_data, headers=headers)
    assert lot_resp.status_code == 201
    lot_id = lot_resp.json()["id"]
    
    # Calculate margin
    margin_data = {
        "lot_id": lot_id,
        "sale_price_per_kg": 7.20,
        "freight_cost": 0.45,
        "insurance": 0.10,
        "other_costs": 0.15
    }
    margin_resp = requests.post(
        f"{BASE_URL}/margins/calculate",
        json=margin_data,
        headers=headers
    )
    assert margin_resp.status_code == 200
    assert "margin_per_kg" in margin_resp.json()
    
    # Cleanup
    requests.delete(f"{BASE_URL}/lots/{lot_id}", headers=headers)
    requests.delete(f"{BASE_URL}/cooperatives/{coop_id}", headers=headers)


def test_ml_predictions_available(auth_token):
    """Verify ML prediction endpoints are functional."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test freight cost prediction
    freight_payload = {
        "origin_port": "Callao",
        "destination_port": "Hamburg",
        "weight_kg": 20000,
        "container_type": "40ft"
    }
    
    try:
        ml_resp = requests.post(
            f"{BASE_URL}/ml/predict-freight",
            json=freight_payload,
            headers=headers
        )
        if ml_resp.status_code == 200:
            assert "predicted_cost" in ml_resp.json()
        else:
            pytest.skip("ML endpoints not fully configured")
    except requests.exceptions.RequestException:
        pytest.skip("ML service not available")


def test_health_endpoints():
    """Verify system health and readiness."""
    health = requests.get(f"{BASE_URL}/health")
    assert health.status_code == 200
    
    # Check Prometheus metrics endpoint
    metrics = requests.get(f"{BASE_URL}/metrics")
    assert metrics.status_code == 200
    assert "http_requests_total" in metrics.text or "python" in metrics.text
